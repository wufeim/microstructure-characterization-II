# Microstructure Characterization II

This is the repository for microstructure characterization research II since May 2019. It consists of two parts:

- **Discriminative**: Feature engineering for microstructure characterization
- **Generative**: Representation learning of microstructure with GANs

## Publication

This repo contains code for reproducing key results in [Image-driven discriminative and generative machine learning algorithms for establishing microstructure-processing relationships](https://doi.org/10.1063/5.0013720).

Our previous work on this topic: [An image-driven machine learning approach to kinetic modeling of a discontinuous precipitation reaction](https://arxiv.org/abs/1906.05496).

## Feature Engineering for Microstructure Characterization

### Microstructure Image Segmentation

To segment a microstructure image, run
```python
import utils
img = utils.segment_image(img)
```

The input image should be in grayscale and the default arguments are:
- ```d=15```: param for bilateral filtering used for segmentation, diameter of each pixel neighborhood
- ```sigma_color=75```: param for bilateral filtering used for segmentation, filter sigma in the color space
- ```sigma_space=75```: param for bilateral filtering used for segmentation, filter sigma in the coordinate space
- ```with_info_bar=True```: boolean, whether to remove info bar from the image using ```utils.crop_image()```

For convenience, a Python script is also provided:
```shell script
python segment_image.py <path_to_image_file>
```
Note: for image filename with spaces, encapsulate the image name by quotation marks:
```shell script
python segment_image.py "datadata/DUM1144 005 500X 30keV HC14 15mm Left 2 LBE 005.png"
```

For demonstration, a sample image is provided: ```data/DUM1144 005 500X 30keV HC14 15mm Left 2 LBE 005.png```.

### Collecting Features

The list of features implemented here are:
- Area features
- Spatial features
- Haralick features (from mahotas)
- LBP features (from scikit-image)

To collect features from image files, run
```python
import features
feature_names = ['area', 'spatial', 'lbp', 'haralick']
f = features.collect_features_by_filenames(filenames, features_names)
```

Default arguments of ```collect_features_by_filenames()``` include:
- ```d=15```: param for bilateral filtering used for segmentation, diameter of each pixel neighborhood
- ```sigma_color=75```: param for bilateral filtering used for segmentation, filter sigma in the color space
- ```sigma_space=75```: param for bilateral filtering used for segmentation, filter sigma in the coordinate space
- ```with_info_bar=True```: boolean, whether to remove info bar from the image using ```utils.crop_image()```
- ```distance=1```: param for haralick features, the distance to consider while computing the occurence matrix
- ```P=10```: param for LBP features, number of circularly symmetric neighbor set points (quantization of the angular space)
- ```R=5```: param for LBP features, radius of circle (spatial resolution of the operator)

The return value of ```collect_features_by_filenames()``` is an ```numpy.ndarray``` of shape m by n, where m is the number of images and n the length of the feature vector. The order of the features names is ignored and the order of the features in the feature vector is area features, spatial features, Haralick features, and LBP features.

### Training and Evaluating a Model

To reproduce the results from the experiments in Section III C, comment/uncomment necessary lines to configure the experiment:
- set of features
- output directory and prefix
- experiments to run

A log file will be saved to the ```<output_dir>```. Trained models, if any, will be saved to ```<model_dir>```. All output files will have ```<output_prefix>``` in the filename.

## Representation Learning with GANs

- **Progressive Growing of GANs**: https://github.com/tkarras/progressive_growing_of_gans
- **Pix2Pix**: https://github.com/phillipi/pix2pix

### Our System

- System: Ubuntu 18.04 NVIDIA RTX Titan
- Environment: Python 3.6.9, TensorFlow 1.13.1
- GPU: NVIDIA RTX Titan

## Other Helper Functions in ```utils.py```

```utils.py``` also provides some helper functions to visualize results from the experiments above. Output images will be saved to the ```figures/``` directory.

### Area Features

<img src="figures/area-features-3d.png" height="60%" width="60%" />

### Confusion Matrix

<img src="figures/binary_classification_results_f1.png" height="60%" width="60%" />
