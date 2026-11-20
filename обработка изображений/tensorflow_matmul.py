#!/usr/bin/env python3

import argparse
import os
import time

import numpy as np
import tensorflow as tf

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

tf.config.set_soft_device_placement(True)
tf.debugging.set_log_device_placement(False)


def has_gpu():
    return bool(tf.config.list_physical_devices("GPU"))


def percentile(sorted_values, q):
    if not sorted_values:
        return float("nan")
    idx = int(round((q / 100.0) * (len(sorted_values) - 1)))
    return sorted_values[idx]


def summarize(samples_ms):
    values = sorted(samples_ms)
    return {
        "count": len(values),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "min": float(values[0]),
        "max": float(values[-1]),
        "p95": float(percentile(values, 95)),
        "std": float(np.std(values)),
    }


def format_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))

    def format_row(values):
        cells = []
        for i, value in enumerate(values):
            text = str(value)
            if i == 0:
                cells.append(text.ljust(widths[i]))
            else:
                cells.append(text.rjust(widths[i]))
        return " | ".join(cells)

    separator = "-+-".join("-" * w for w in widths)
    lines = [format_row(headers), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def benchmark_op(op_fn, warmup, runs):
    for _ in range(warmup):
        op_fn().numpy()

    samples_ms = []
    for _ in range(runs):
        t0 = time.perf_counter()
        op_fn().numpy()
        t1 = time.perf_counter()
        samples_ms.append((t1 - t0) * 1000.0)

    return summarize(samples_ms)


def build_ops(device, n, dtype):
    with tf.device(device):
        a = tf.random.normal((n, n), dtype=dtype)
        b = tf.random.normal((n, n), dtype=dtype)
        x = tf.random.normal((n, n), dtype=dtype)
        y = tf.random.normal((n, n), dtype=dtype)
        m3_a = tf.random.normal((32, 256, 256), dtype=dtype)
        m3_b = tf.random.normal((32, 256, 256), dtype=dtype)
        m4 = tf.random.normal((64, 64, 64, 64), dtype=dtype)
        img = tf.random.normal((1, 512, 512, 3), dtype=dtype)
        ker = tf.random.normal((3, 3, 3, 32), dtype=dtype)
        dw_ker = tf.random.normal((3, 3, 3, 2), dtype=dtype)

    @tf.function
    def op_matmul():
        out = tf.matmul(a, b)
        return tf.reduce_sum(out)

    @tf.function
    def op_batched_matmul():
        out = tf.matmul(m3_a, m3_b)
        return tf.reduce_sum(out)

    @tf.function
    def op_add():
        out = x + y
        return tf.reduce_sum(out)

    @tf.function
    def op_relu():
        out = tf.nn.relu(x)
        return tf.reduce_sum(out)

    @tf.function
    def op_sigmoid():
        out = tf.nn.sigmoid(x)
        return tf.reduce_sum(out)

    @tf.function
    def op_tanh():
        out = tf.nn.tanh(x)
        return tf.reduce_sum(out)

    @tf.function
    def op_softmax():
        out = tf.nn.softmax(x, axis=1)
        return tf.reduce_sum(out)

    @tf.function
    def op_exp_log():
        out = tf.math.log(tf.math.exp(tf.abs(x)) + tf.cast(1e-6, dtype))
        return tf.reduce_sum(out)

    @tf.function
    def op_reduce_sum():
        out = tf.reduce_sum(m4, axis=[2, 3])
        return tf.reduce_sum(out)

    @tf.function
    def op_transpose():
        out = tf.transpose(m4, perm=[0, 2, 3, 1])
        return tf.reduce_sum(out)

    @tf.function
    def op_square_sqrt():
        out = tf.sqrt(tf.square(x) + tf.cast(1e-6, dtype))
        return tf.reduce_sum(out)

    @tf.function
    def op_conv2d():
        out = tf.nn.conv2d(img, ker, strides=[1, 1, 1, 1], padding="SAME")
        return tf.reduce_sum(out)

    @tf.function
    def op_depthwise_conv2d():
        out = tf.nn.depthwise_conv2d(img, dw_ker, strides=[1, 1, 1, 1], padding="SAME")
        return tf.reduce_sum(out)

    return {
        "matmul": op_matmul,
        "batched_matmul": op_batched_matmul,
        "add": op_add,
        "relu": op_relu,
        "sigmoid": op_sigmoid,
        "tanh": op_tanh,
        "softmax": op_softmax,
        "exp_log": op_exp_log,
        "reduce_sum": op_reduce_sum,
        "transpose": op_transpose,
        "square_sqrt": op_square_sqrt,
        "conv2d": op_conv2d,
        "depthwise_conv2d": op_depthwise_conv2d,
    }


def main():
    parser = argparse.ArgumentParser(description="CPU vs GPU TensorFlow benchmark")
    parser.add_argument("--size", type=int, default=4096, help="Matrix size for matmul/add/relu")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup runs per operation")
    parser.add_argument("--runs", type=int, default=30, help="Measured runs per operation")
    parser.add_argument(
        "--dtype",
        type=str,
        default="float32",
        choices=["float32", "float64"],
        help="Tensor dtype",
    )
    args, _ = parser.parse_known_args()

    dtype = tf.float32 if args.dtype == "float32" else tf.float64
    devices = ["/CPU:0"]
    if has_gpu():
        devices.append("/GPU:0")

    all_stats = {}
    print("TensorFlow version:", tf.__version__)
    print("Benchmark config: size={}, warmup={}, runs={}, dtype={}".format(args.size, args.warmup, args.runs, args.dtype))
    print()

    for device in devices:
        label = "CPU" if device == "/CPU:0" else "GPU"
        ops = build_ops(device, args.size, dtype)
        all_stats[label] = {}
        rows = []

        for op_name, op_fn in ops.items():
            stats = benchmark_op(op_fn, args.warmup, args.runs)
            all_stats[label][op_name] = stats
            rows.append(
                [
                    op_name,
                    stats["count"],
                    "{:.3f}".format(stats["mean"]),
                    "{:.3f}".format(stats["median"]),
                    "{:.3f}".format(stats["p95"]),
                    "{:.3f}".format(stats["min"]),
                    "{:.3f}".format(stats["max"]),
                    "{:.3f}".format(stats["std"]),
                ]
            )

        print("{} results (ms):".format(label))
        print(
            format_table(
                ["op", "runs", "mean", "median", "p95", "min", "max", "std"],
                rows,
            )
        )
        print()

    if "CPU" in all_stats and "GPU" in all_stats:
        print("GPU speedup over CPU (median-based):")
        speedup_rows = []
        for op_name in all_stats["CPU"]:
            cpu_median = all_stats["CPU"][op_name]["median"]
            gpu_median = all_stats["GPU"][op_name]["median"]
            speedup = cpu_median / gpu_median if gpu_median > 0 else float("inf")
            speedup_rows.append(
                [
                    op_name,
                    "{:.3f}".format(cpu_median),
                    "{:.3f}".format(gpu_median),
                    "{:.2f}x".format(speedup),
                ]
            )
        print(format_table(["op", "cpu_median_ms", "gpu_median_ms", "speedup"], speedup_rows))


if __name__ == "__main__":
    main()
