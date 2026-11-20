
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import glob
import os

def extract_features(image_path):
    """
    Extract color standard deviation features from HSV and YCrCb color spaces.

    Parameters:
    -----------
    image_path : str
        Path to the input image

    Returns:
    --------
    dict : Dictionary containing 6 standard deviation features
    """
    # 1. Load Image (OpenCV loads as BGR by default)
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return None

    # 2. Convert to HSV
    # OpenCV Ranges: H (0-179), S (0-255), V (0-255)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(img_hsv)

    # 3. Convert to YCrCb (Note: OpenCV uses YCrCb ordering)
    # OpenCV Ranges: Y, Cr, Cb (all 0-255)
    img_ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(img_ycrcb)

    # 4. Compute Standard Deviation (flattening happens automatically with np.std)
    features = {
        'sd_Hue': np.std(h),
        'sd_Saturation': np.std(s),
        'sd_Value': np.std(v),
        'sd_Y': np.std(y),
        'sd_Cr': np.std(cr),
        'sd_Cb': np.std(cb)
    }

    return features


def build_dataset(image_folder):
    """
    Extract features from all images in a folder and return a DataFrame.

    Parameters:
    -----------
    image_folder : str
        Path to folder containing images

    Returns:
    --------
    pd.DataFrame : DataFrame with extracted features
    """
    data = []
    files = glob.glob(os.path.join(image_folder, "*.*"))

    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            feats = extract_features(f)
            if feats:
                feats['filename'] = os.path.basename(f)
                data.append(feats)

    df = pd.DataFrame(data)
    return df


def normalize_features(df, method='minmax'):
    """
    Normalize feature columns using specified method.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with features to normalize
    method : str
        'minmax' for Min-Max Scaling (0-1 range)
        'standard' for Standardization (mean=0, std=1)

    Returns:
    --------
    pd.DataFrame : DataFrame with normalized features
    tuple : (scaler object, feature columns)
    """
    # Get feature columns (exclude non-numeric columns like 'filename')
    feature_cols = [col for col in df.columns if col.startswith('sd_')]

    # Create a copy to avoid modifying original
    df_normalized = df.copy()

    if method == 'minmax':
        # Min-Max Scaling: scales to [0, 1]
        # Best for: Neural networks, bounded features, preserving distribution shape
        scaler = MinMaxScaler()
        df_normalized[feature_cols] = scaler.fit_transform(df[feature_cols])

    elif method == 'standard':
        # Standardization (Z-score): centers at mean=0, std=1
        # Best for: PCA, SVM, algorithms assuming Gaussian distribution
        scaler = StandardScaler()
        df_normalized[feature_cols] = scaler.fit_transform(df[feature_cols])

    else:
        raise ValueError("Method must be 'minmax' or 'standard'")

    return df_normalized, scaler, feature_cols


def plot_feature_distributions(df, df_normalized, save_prefix='feature_plots'):
    """
    Create comprehensive visualization of feature distributions.

    Parameters:
    -----------
    df : pd.DataFrame
        Original (unnormalized) features
    df_normalized : pd.DataFrame
        Normalized features
    save_prefix : str
        Prefix for saved plot filenames
    """
    feature_cols = [col for col in df.columns if col.startswith('sd_')]

    # Define custom color palette (professional and distinct)
    colors = {
        'sd_Hue': '#E63946',          # Red
        'sd_Saturation': '#F77F00',   # Orange
        'sd_Value': '#FCBF49',        # Yellow
        'sd_Y': '#06A77D',            # Green
        'sd_Cr': '#118AB2',           # Blue
        'sd_Cb': '#8338EC'            # Purple
    }

    # Feature descriptions for labels
    descriptions = {
        'sd_Hue': 'SD(Hue)\nColor Diversity',
        'sd_Saturation': 'SD(Saturation)\nVividness Range',
        'sd_Value': 'SD(Value)\nBrightness Contrast',
        'sd_Y': 'SD(Y)\nLuminance Variation',
        'sd_Cr': 'SD(Cr)\nRed-Green Balance',
        'sd_Cb': 'SD(Cb)\nBlue-Yellow Balance'
    }

    # ===== PLOT 1: Box Plot Comparison (Original vs Normalized) =====
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Original features
    df_melt_orig = df[feature_cols].melt(var_name='Feature', value_name='Standard Deviation')
    color_list_orig = [colors[f] for f in feature_cols]

    sns.boxplot(x='Feature', y='Standard Deviation', data=df_melt_orig, 
                palette=color_list_orig, ax=axes[0], linewidth=2)
    axes[0].set_title('Original Feature Distributions (Unnormalized)', 
                      fontsize=14, fontweight='bold', pad=20)
    axes[0].set_xlabel('Color Channel Features', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Standard Deviation (pixel units)', fontsize=12, fontweight='bold')
    axes[0].set_xticklabels([descriptions[f] for f in feature_cols], fontsize=10)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Normalized features
    df_melt_norm = df_normalized[feature_cols].melt(var_name='Feature', value_name='Normalized Value')

    sns.boxplot(x='Feature', y='Normalized Value', data=df_melt_norm, 
                palette=color_list_orig, ax=axes[1], linewidth=2)
    axes[1].set_title('Normalized Feature Distributions (Min-Max [0,1])', 
                      fontsize=14, fontweight='bold', pad=20)
    axes[1].set_xlabel('Color Channel Features', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Normalized Value [0-1]', fontsize=12, fontweight='bold')
    axes[1].set_xticklabels([descriptions[f] for f in feature_cols], fontsize=10)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{save_prefix}_boxplot_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # ===== PLOT 2: Correlation Heatmap (Normalized Features) =====
    plt.figure(figsize=(10, 8))
    corr_matrix = df_normalized[feature_cols].corr()

    # Create custom labels with descriptions
    short_labels = ['Hue', 'Saturation', 'Value', 'Y', 'Cr', 'Cb']

    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)  # Upper triangle mask

    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r', 
                center=0, vmin=-1, vmax=1, square=True, mask=mask,
                linewidths=2, cbar_kws={"shrink": 0.8, "label": "Correlation Coefficient"},
                xticklabels=short_labels, yticklabels=short_labels)

    plt.title('Feature Correlation Matrix\n(Normalized Features)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Features', fontsize=12, fontweight='bold')
    plt.ylabel('Features', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(f'{save_prefix}_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    # ===== PLOT 3: Violin Plot (Normalized - Shows density) =====
    fig, ax = plt.subplots(figsize=(14, 7))

    sns.violinplot(x='Feature', y='Normalized Value', data=df_melt_norm, 
                   palette=color_list_orig, inner='quartile', linewidth=2, ax=ax)

    ax.set_title('Feature Value Distributions (Density + Quartiles)\nNormalized to [0,1] Range', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Color Channel Features', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Value [0-1]', fontsize=12, fontweight='bold')
    ax.set_xticklabels([descriptions[f] for f in feature_cols], fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add reference line at 0.5
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Midpoint (0.5)')
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(f'{save_prefix}_violin_plot.png', dpi=300, bbox_inches='tight')
    plt.close()

    # ===== PLOT 4: Pair Plot (Scatter Matrix) - Shows relationships =====
    # Note: This can be slow for large datasets, consider sampling
    if len(df_normalized) > 500:
        sample_df = df_normalized.sample(n=500, random_state=42)
    else:
        sample_df = df_normalized

    # Create pair plot with custom styling
    pairplot = sns.pairplot(sample_df[feature_cols], diag_kind='kde', corner=True,
                            plot_kws={'alpha': 0.6, 's': 30, 'edgecolor': 'k', 'linewidth': 0.5},
                            diag_kws={'linewidth': 2, 'color': '#2E86AB'})

    pairplot.fig.suptitle('Feature Interaction Matrix (Pairwise Scatter Plots)\nNormalized Features', 
                          fontsize=14, fontweight='bold', y=1.02)

    plt.savefig(f'{save_prefix}_pairplot.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"All plots saved with prefix: {save_prefix}")
    return colors, descriptions


# ===== USAGE EXAMPLE =====
# Uncomment and modify the path below:
df = build_dataset("tapochki_photos/preprocessed/")
df_normalized, scaler, feature_cols = normalize_features(df, method='minmax')
plot_feature_distributions(df, df_normalized, save_prefix='my_analysis')
# 
# # Save normalized features to CSV
# df_normalized.to_csv('normalized_features.csv', index=False)
# 
# # To use the scaler on new images:
# new_img_features = extract_features("new_image.jpg")
# new_features_array = np.array([[new_img_features[col] for col in feature_cols]])
# new_normalized = scaler.transform(new_features_array)
