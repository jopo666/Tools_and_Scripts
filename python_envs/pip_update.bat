@ECHO OFF

python -m pip install --upgrade pip setuptools wheel

pip install tifffile -U
pip install czifile -U
pip install aicsimageio -U
pip install aicspylibczi -U
pip install pydash -U
pip install lxml -U
#pip install progressbar2 -U
#pip install seaborn -U
#pip install pandas -U
#pip install matplotlib -U
pip install magicgui -U
pip install napari -U
pip install ome-zarr -U
#pip install numpy==1.18.5
pip install scikit-image -U
pip install apeer-dev-kit -U
pip install apeer-ometiff-library -U
pip install ipywidgets -U