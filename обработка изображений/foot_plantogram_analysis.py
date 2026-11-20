"""
Foot Plantogram Analysis Pipeline
=================================
This module provides tools for analyzing foot plantograms captured with green LED illumination.

Key Features:
- Foot segmentation from background
- Left/Right foot separation
- Length and width measurements
- Contact area analysis (pressure zones)
- Preparation for orthopedic coefficient calculation

Author: Medical Image Processing Project
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Optional, List
import os


@dataclass
class FootMeasurements:
    """Container for foot measurements in pixels and mm (if calibrated)."""
    length_px: float  # Maximum length in pixels
    width_px: float   # Maximum width in pixels
    contact_area_px: int  # Contact area in pixels
    total_area_px: int  # Total foot area in pixels
    contact_ratio: float  # Ratio of contact to total area
    
    # Calibrated measurements (set if pixels_per_mm is known)
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    contact_area_mm2: Optional[float] = None
    
    # Bounding box
    bbox: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
    
    # Contour for further analysis
    contour: Optional[np.ndarray] = None


class PlantogramAnalyzer:
    """
    Analyzer for foot plantogram images captured with green LED illumination.
    
    The green channel carries the most information about foot contact pressure.
    """
    
    def __init__(self, pixels_per_mm: Optional[float] = None):
        """
        Initialize the analyzer.
        
        Parameters:
        -----------
        pixels_per_mm : float, optional
            Calibration factor for converting pixels to millimeters.
            If None, measurements will be in pixels only.
        """
        self.pixels_per_mm = pixels_per_mm
        
    def load_image(self, image_path: str) -> np.ndarray:
        """Load an image from file."""
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
        # Convert BGR to RGB for display
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def split_feet(self, image: np.ndarray, 
                   left_crop: int = 280, 
                   right_crop: int = 290,
                   center_gap_start: int = 880,
                   center_gap_end: int = 1025) -> Tuple[np.ndarray, np.ndarray]:
        """
        Split image into left and right foot regions.
        
        Parameters based on standard podoscanner output (1920x1080).
        Returns: (right_foot_image, left_foot_image)
        """
        h, w = image.shape[:2]
        
        # Right foot (anatomically) is on the left side of image
        right_foot = image[:, left_crop:center_gap_start, :]
        
        # Left foot (anatomically) is on the right side of image
        left_foot = image[:, center_gap_end:(w - right_crop), :]
        
        return right_foot, left_foot
    
    def segment_foot(self, image: np.ndarray, 
                     method: str = 'green_channel',
                     threshold: int = 30,
                     use_adaptive: bool = False) -> np.ndarray:
        """
        Segment foot from background using green channel.
        
        Parameters:
        -----------
        image : np.ndarray
            RGB foot image
        method : str
            'green_channel' - use green channel directly
            'hsv' - use HSV color space for green detection
            'combined' - combine multiple methods
        threshold : int
            Threshold value for binarization
        use_adaptive : bool
            Use adaptive thresholding instead of global
            
        Returns:
        --------
        np.ndarray : Binary mask of the foot
        """
        if method == 'green_channel':
            # Green channel contains the contact information
            green = image[:, :, 1]
            
            if use_adaptive:
                # Adaptive threshold works better for uneven illumination
                mask = cv2.adaptiveThreshold(
                    green, 255, 
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    blockSize=51, C=-10
                )
            else:
                _, mask = cv2.threshold(green, threshold, 255, cv2.THRESH_BINARY)
                
        elif method == 'hsv':
            # Convert to HSV and filter green hues
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Green range in HSV (adjust based on your LED)
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])
            
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
        elif method == 'combined':
            # Combine green channel and HSV methods
            green_mask = self.segment_foot(image, method='green_channel', 
                                           threshold=threshold)
            hsv_mask = self.segment_foot(image, method='hsv')
            
            # Take union of both masks
            mask = cv2.bitwise_or(green_mask, hsv_mask)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Clean up the mask with morphological operations
        mask = self._clean_mask(mask)
        
        return mask
    
    def _clean_mask(self, mask: np.ndarray, 
                    kernel_size: int = 5,
                    min_area: int = 1000) -> np.ndarray:
        """
        Clean binary mask using morphological operations.
        
        - Removes small noise
        - Fills small holes
        - Smooths edges
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, 
                                           (kernel_size, kernel_size))
        
        # Close small holes
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Remove small noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Keep only the largest connected component (the foot)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Filter by minimum area and keep largest
            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            if valid_contours:
                largest = max(valid_contours, key=cv2.contourArea)
                mask = np.zeros_like(mask)
                cv2.drawContours(mask, [largest], -1, 255, -1)
        
        return mask
    
    def get_foot_contour(self, mask: np.ndarray) -> Optional[np.ndarray]:
        """Extract the main foot contour from binary mask."""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        return max(contours, key=cv2.contourArea)
    
    def segment_contact_area(self, image: np.ndarray, 
                             foot_mask: np.ndarray,
                             intensity_threshold: int = 80) -> np.ndarray:
        """
        Segment the contact area (high pressure zones) within the foot.
        
        These are the brighter green areas where the foot presses harder.
        
        Parameters:
        -----------
        image : np.ndarray
            RGB foot image
        foot_mask : np.ndarray
            Binary mask of the foot outline
        intensity_threshold : int
            Minimum green intensity to be considered contact area
            
        Returns:
        --------
        np.ndarray : Binary mask of contact areas
        """
        green = image[:, :, 1]
        
        # Apply foot mask first
        masked_green = cv2.bitwise_and(green, green, mask=foot_mask)
        
        # Threshold for high intensity (contact) areas
        _, contact_mask = cv2.threshold(masked_green, intensity_threshold, 
                                         255, cv2.THRESH_BINARY)
        
        return contact_mask
    
    def measure_foot(self, image: np.ndarray, 
                     foot_mask: np.ndarray,
                     contact_mask: Optional[np.ndarray] = None) -> FootMeasurements:
        """
        Calculate foot measurements from masks.
        
        Parameters:
        -----------
        image : np.ndarray
            Original RGB image
        foot_mask : np.ndarray
            Binary mask of foot outline
        contact_mask : np.ndarray, optional
            Binary mask of contact areas
            
        Returns:
        --------
        FootMeasurements : Dataclass with all measurements
        """
        contour = self.get_foot_contour(foot_mask)
        
        if contour is None:
            raise ValueError("No foot contour found in mask")
        
        # Bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Rotated bounding box for more accurate length/width
        rect = cv2.minAreaRect(contour)
        (cx, cy), (width, height), angle = rect
        
        # Length is the longer dimension, width is shorter
        length_px = max(width, height)
        width_px = min(width, height)
        
        # Areas
        total_area_px = cv2.contourArea(contour)
        
        if contact_mask is not None:
            contact_area_px = np.sum(contact_mask > 0)
        else:
            contact_area_px = total_area_px
        
        contact_ratio = contact_area_px / total_area_px if total_area_px > 0 else 0
        
        # Create measurements object
        measurements = FootMeasurements(
            length_px=length_px,
            width_px=width_px,
            contact_area_px=contact_area_px,
            total_area_px=total_area_px,
            contact_ratio=contact_ratio,
            bbox=(x, y, w, h),
            contour=contour
        )
        
        # Add calibrated measurements if available
        if self.pixels_per_mm is not None:
            measurements.length_mm = length_px / self.pixels_per_mm
            measurements.width_mm = width_px / self.pixels_per_mm
            measurements.contact_area_mm2 = contact_area_px / (self.pixels_per_mm ** 2)
        
        return measurements
    
    def calculate_arch_index(self, contact_mask: np.ndarray, 
                             foot_mask: np.ndarray) -> float:
        """
        Calculate the Arch Index (Cavanagh & Rodgers, 1987).
        
        Divides foot into thirds (heel, midfoot, forefoot) and calculates:
        AI = midfoot_contact_area / total_contact_area
        
        AI < 0.21 = High arch (pes cavus)
        AI 0.21-0.26 = Normal arch
        AI > 0.26 = Flat foot (pes planus)
        
        Returns:
        --------
        float : Arch index value
        """
        contour = self.get_foot_contour(foot_mask)
        if contour is None:
            return -1
        
        x, y, w, h = cv2.boundingRect(contour)
        
        # Divide into thirds along the length (y-axis for typical foot orientation)
        third_height = h // 3
        
        # Create masks for each region
        heel_mask = np.zeros_like(foot_mask)
        midfoot_mask = np.zeros_like(foot_mask)
        forefoot_mask = np.zeros_like(foot_mask)
        
        heel_mask[y + 2*third_height:y + h, :] = 255
        midfoot_mask[y + third_height:y + 2*third_height, :] = 255
        forefoot_mask[y:y + third_height, :] = 255
        
        # Apply to contact mask
        heel_contact = cv2.bitwise_and(contact_mask, heel_mask)
        midfoot_contact = cv2.bitwise_and(contact_mask, midfoot_mask)
        forefoot_contact = cv2.bitwise_and(contact_mask, forefoot_mask)
        
        # Calculate areas
        total_contact = np.sum(contact_mask > 0)
        midfoot_area = np.sum(midfoot_contact > 0)
        
        if total_contact == 0:
            return -1
        
        arch_index = midfoot_area / total_contact
        
        return arch_index
    
    def calculate_staheli_index(self, contact_mask: np.ndarray,
                                 foot_mask: np.ndarray) -> float:
        """
        Calculate the Staheli Index (Staheli et al., 1987).
        
        SI = narrowest_midfoot_width / widest_heel_width
        
        SI < 0.50 = Normal arch
        SI 0.50-1.0 = Low arch
        SI > 1.0 = Flat foot
        
        Returns:
        --------
        float : Staheli index value
        """
        contour = self.get_foot_contour(foot_mask)
        if contour is None:
            return -1
        
        x, y, w, h = cv2.boundingRect(contour)
        
        # Find the narrowest point in midfoot region
        third_height = h // 3
        midfoot_start = y + third_height
        midfoot_end = y + 2 * third_height
        
        # Heel region
        heel_start = y + 2 * third_height
        heel_end = y + h
        
        # Calculate width at each row
        min_midfoot_width = float('inf')
        max_heel_width = 0
        
        for row in range(midfoot_start, midfoot_end):
            row_pixels = np.sum(contact_mask[row, :] > 0)
            if 0 < row_pixels < min_midfoot_width:
                min_midfoot_width = row_pixels
        
        for row in range(heel_start, heel_end):
            row_pixels = np.sum(contact_mask[row, :] > 0)
            if row_pixels > max_heel_width:
                max_heel_width = row_pixels
        
        if max_heel_width == 0:
            return -1
        
        return min_midfoot_width / max_heel_width
    
    def visualize_analysis(self, image: np.ndarray, 
                           foot_mask: np.ndarray,
                           contact_mask: np.ndarray,
                           measurements: FootMeasurements,
                           title: str = "Foot Analysis") -> plt.Figure:
        """
        Create a comprehensive visualization of the analysis.
        
        Returns a matplotlib Figure with multiple subplots.
        """
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle(title, fontsize=14)
        
        # Original image
        axes[0, 0].imshow(image)
        axes[0, 0].set_title("Original Image")
        axes[0, 0].axis('off')
        
        # Green channel
        axes[0, 1].imshow(image[:, :, 1], cmap='Greens')
        axes[0, 1].set_title("Green Channel")
        axes[0, 1].axis('off')
        
        # Foot mask
        axes[0, 2].imshow(foot_mask, cmap='gray')
        axes[0, 2].set_title("Foot Segmentation")
        axes[0, 2].axis('off')
        
        # Contact area
        axes[1, 0].imshow(contact_mask, cmap='hot')
        axes[1, 0].set_title("Contact Area")
        axes[1, 0].axis('off')
        
        # Overlay contour on original
        overlay = image.copy()
        if measurements.contour is not None:
            cv2.drawContours(overlay, [measurements.contour], -1, (255, 0, 0), 3)
            # Draw bounding box
            x, y, w, h = measurements.bbox
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 255), 2)
        axes[1, 1].imshow(overlay)
        axes[1, 1].set_title("Contour Detection")
        axes[1, 1].axis('off')
        
        # Measurements text
        axes[1, 2].axis('off')
        text = f"""
        Foot Measurements
        ─────────────────
        Length: {measurements.length_px:.1f} px
        Width: {measurements.width_px:.1f} px
        
        Total Area: {measurements.total_area_px:,} px²
        Contact Area: {measurements.contact_area_px:,} px²
        Contact Ratio: {measurements.contact_ratio:.2%}
        """
        
        if measurements.length_mm is not None:
            text += f"""
        ─────────────────
        Calibrated:
        Length: {measurements.length_mm:.1f} mm
        Width: {measurements.width_mm:.1f} mm
        Contact: {measurements.contact_area_mm2:.1f} mm²
        """
        
        axes[1, 2].text(0.1, 0.5, text, transform=axes[1, 2].transAxes,
                        fontsize=12, verticalalignment='center',
                        fontfamily='monospace',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    def analyze_plantogram(self, image_path: str,
                           segment_threshold: int = 30,
                           contact_threshold: int = 80,
                           visualize: bool = True) -> dict:
        """
        Complete analysis pipeline for a plantogram image.
        
        Parameters:
        -----------
        image_path : str
            Path to the plantogram image
        segment_threshold : int
            Threshold for foot segmentation
        contact_threshold : int
            Threshold for contact area detection
        visualize : bool
            Whether to create visualization plots
            
        Returns:
        --------
        dict : Dictionary containing all analysis results
        """
        # Load image
        image = self.load_image(image_path)
        
        # Split into left and right feet
        right_foot, left_foot = self.split_feet(image)
        
        results = {'image_path': image_path}
        
        for name, foot_img in [('right', right_foot), ('left', left_foot)]:
            # Segment foot
            foot_mask = self.segment_foot(foot_img, threshold=segment_threshold)
            
            # Segment contact area
            contact_mask = self.segment_contact_area(foot_img, foot_mask, 
                                                      contact_threshold)
            
            # Get measurements
            try:
                measurements = self.measure_foot(foot_img, foot_mask, contact_mask)
                
                # Calculate indices
                arch_index = self.calculate_arch_index(contact_mask, foot_mask)
                staheli_index = self.calculate_staheli_index(contact_mask, foot_mask)
                
                results[f'{name}_foot'] = {
                    'measurements': measurements,
                    'arch_index': arch_index,
                    'staheli_index': staheli_index,
                    'mask': foot_mask,
                    'contact_mask': contact_mask,
                    'image': foot_img
                }
                
                if visualize:
                    fig = self.visualize_analysis(
                        foot_img, foot_mask, contact_mask, measurements,
                        title=f"{name.capitalize()} Foot Analysis"
                    )
                    results[f'{name}_figure'] = fig
                    
            except ValueError as e:
                print(f"Warning: Could not analyze {name} foot: {e}")
                results[f'{name}_foot'] = None
        
        return results


def demo_analysis():
    """Demonstrate the analysis pipeline."""
    # Example usage
    analyzer = PlantogramAnalyzer(pixels_per_mm=None)  # Set calibration if known
    
    # Path to example image - update this to your image
    image_path = "/home/dima/Documents/альбрехт/обработка изображений/плантограммы/Img.png"
    
    if os.path.exists(image_path):
        results = analyzer.analyze_plantogram(image_path, visualize=True)
        
        for foot_name in ['left_foot', 'right_foot']:
            if results.get(foot_name):
                m = results[foot_name]['measurements']
                ai = results[foot_name]['arch_index']
                si = results[foot_name]['staheli_index']
                
                print(f"\n{foot_name.upper()}")
                print(f"  Length: {m.length_px:.1f} px")
                print(f"  Width: {m.width_px:.1f} px")
                print(f"  Contact Ratio: {m.contact_ratio:.2%}")
                print(f"  Arch Index: {ai:.3f}")
                print(f"  Staheli Index: {si:.3f}")
        
        plt.show()
    else:
        print(f"Demo image not found: {image_path}")
        print("Please update the path to your plantogram image.")


if __name__ == "__main__":
    demo_analysis()
