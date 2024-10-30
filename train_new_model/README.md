# Buildings detection using "detectron2" model developed by META

## Roboflow is a end-to-end computer vision tool, and we used it in our work.

## Architecture

1. This project aims to detect buildings from the satellite images.
2. The architecture used is called GeneralizedRCNN (Region-Based Convolutional Neural Network).
3. This architecture conists of three blocks

   ### Feature Pyramid Network (FPN)
   ### Region Proposal Network (RPN)
   ### ROI Heads

#### Detailed explination of each block is present in "https://medium.com/@hirotoschwert/digging-into-detectron-2-47b2e794fabd".

## Dataset

The dataset we considered is 'building-detection Image Dataset' from Roboflow.

## Code

code is available in the build-seg.ipynb file.

*Adjust the file paths before executing*

## Results
Results are available in the results folder.
