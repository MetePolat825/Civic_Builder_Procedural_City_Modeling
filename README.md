# Civic Builder: AI-Powered Urban 3D Modelling Solution

<div align="center">
  <a href="https://github.com/MetePolat825/Civic_Builder_Procedural_City_Modeling">
    <img src="documentation/media/civic_builder.png" alt="Logo" width="200" height="200">
  </a>
</div>

# Project Introduction

Creating realistic 3D city environments is a complex and time-consuming process, often requiring specialized GIS software, extensive manual effort, and high-end computing resources. This can be a significant barrier for game developers, urban planners, and simulation engineers looking to integrate real-world city layouts into their projects.
  
Civic Builder is an AI-driven city modeling tool that automates the generation of urban environments using machine learning and computer vision. By leveraging satellite imagery and GIS datasets, it enables the procedural creation of customizable, realistic city layouts. Designed for seamless integration with game engines and simulation platforms, Civic Builder provides an efficient and scalable solution for urban modeling.

![Building Detection Image](https://miro.medium.com/v2/resize:fit:3726/format:webp/1*gQbpjPrERFqM4UwODSqQKQ.png)


## Key Features

- Automated City Generation: Uses AI to analyze GIS data and satellite imagery to generate 3D models of urban environments.

- Customizable Layouts: Supports varying levels of detail, from dense metropolitan areas to suburban and rural layouts.

- Integration with Game Engines: Exports to formats compatible with Unreal Engine, Unity, and Blender.

- Real-World Accuracy: Utilizes open-source GIS datasets to create precise representations of real-world cities.

- Scalable and Performant: Optimized for large-scale city generation while maintaining high visual fidelity.

- Cross-Platform Support: Runs on local machines as well as cloud-based processing environments.

# Demo

Check out a demo on YouTube!

![Civic Builder Demo Video]([https://img.youtube.com/vi/Of_KlHj6Tgo/0.jpg](https://www.youtube.com/watch?v=Of_KlHj6Tgo))

**Thanks for the thumbs up 😀👍**

# Step-by-Step Usage

### 1. Upload Imagery Data:
Upload satellite imagery or GIS dataset files (GeoJSON, Shapefiles, etc.) to begin the city generation process.

### 2.Process the Data: 
The AI engine extracts building footprints, road networks, and land use classifications to construct a detailed city model.

### 3.Export the Models (Feature + Imagery): 
Download the generated 3D city as an FBX, OBJ, or glTF file, ready for import into game engines or 3D modeling software.

Example Output: After processing, Civic Builder generates the following items:

- features.fbx -> contains extracted features, one per file, named appropriately.
- imagery.fbx -> polygonized representation of the imagery initially uploaded, seamlessly compatible with the generated features to be used for immediate visualization.

# Getting Started

Follow these instructions to set up Civic Builder on your local machine for development and testing.

## Prerequisites

To run this project locally, you need the following installed on your machine:

- Python 3.8+

- pip (Python package manager)

- Blender (optional for direct integration)

Dependancies can be installed by running pip install requirements.txt

# Installation and Running Instructions

If you wish to deploy the application locally on your machine, here is a step by step series of examples that tell you how to get a development env running in no time!

## 1. Clone the repository
```bash
git clone https://github.com/MetePolat825/Civic_Builder_Procedural_City_Modeling.git
```

## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Navigate to the application folder
```bash
cd application
```

## 4. Run the Flask app on the local server 127.0.0.1:5000
```bash
python main.py
```

## 5. (Optional) Build the application locally using Pyinstaller
If you wish to access the application via an executable, you can build a local version using Pyinstaller.

# Built With

* AI Model: Meta Detectron 2

* Python

* Blender API for the Blender plugin

* UI: customtkinter library ![customtkinter](https://github.com/TomSchimansky/CustomTkinter).

# Project Folder Structure

```bash
├── backend
   ├── presets <- PBR value preset CSVs
   ├── processed <- final processed images to be downloaded to the user
   ├── src <- image processing scripts and other secondary logic
   ├── static <- images, icons, CSS
   ├── templates <- frontend HTML templates
   ├── tests <- unit tests for app and image processing logic
   ├── uploads <- user upload directory
   ├── app.py <- Entry Point for the program
├── frontend <- contains Javascript frontend components (work in progress)
├── docs <- contains local copy of documentation for offline access
├── README.md <- Developer Documentation
├── requirements.txt <- required libraries for local installation
```

# Roadmap

## Future Features:

- AI-powered procedural generation for varied architectural styles.

- API for dynamic city generation in real-time applications.

- Improved building material and texture generation.

- Cloud-based rendering for large-scale urban simulations.

# Contributing

We welcome contributions! Please read our Contributing Guidelines and Code of Conduct before getting started.

1. Fork the repository.

2. Create a new branch for your feature or bugfix.

3. Make your changes and test them thoroughly.

4. Submit a pull request with a detailed description of your changes.

# Authors

* **MetePolat825** - *Initial work* - [MetePolat825](https://github.com/MetePolat825)

See also the list of [contributors](https://github.com/MetePolat825/MapMorph_Web_App_PBR_Texture_Generation/contributors) who participated in this project.

# License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

# Acknowledgments
* Meta for Meta Detectron 2 detection model.

* OpenCV for image processing.

* Best README Template for inspiration.
