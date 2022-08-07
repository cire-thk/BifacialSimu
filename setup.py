from setuptools import setup,find_packages,Extension
from setuptools import find_packages
from codecs import open
from os import path

# ======== WAS CAUSING AN ERROR, COMMENTED OUT FOR NOW ========================
# # Load the README file.
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# ERORR GIVE:
# Traceback (most recent call last):
#   File "C:\Users\faris\OneDrive\Documents\GitHub\BifacialSimu\setup.py", line 7, in <module>
#     long__description = readme_handle.read()
#   File "C:\Users\faris\anaconda3\lib\encodings\cp1252.py", line 23, in decode
#     return codecs.charmap_decode(input,self.errors,decoding_table)[0]
# UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 4073: character maps to <undefined>
# =============================================================================

setup(
    

    # Define the library name, this is what is used along with `pip install`.
    name='BifacialSimu',

    # Define the author of the repository.
    author='Eva-Maria Grommes',

    # Define the Author's email, so people know who to reach out to.
    author_email='Eva-Maria.Grommes@th-koeln.de',

    # Define the version of this library.
    # Read this as
    #   - MAJOR VERSION 1
    #   - MINOR VERSION 0
    #   - MAINTENANCE VERSION 0
    version='1.0.0',

    # Here is a small description of the library. This appears
    # when someone searches for the library on https://pypi.org/search.
    description='Hollistic Simulation of large-scale Bifacial Photovoltaic Systems',

    # I have a long description but that will just be my README
    # file, note the variable up above where I read the file.
    long_description=long_description,

    # This will specify that the long description is MARKDOWN.
    long_description_content_type="text/markdown",

    # Here is the URL where you can find the code, in this case on GitHub.
    url='https://github.com/cire-thk/BifacialSimu',

    # These are the dependencies the library needs in order to run.
    install_requires=[
        'pandas==1.3.4',
        'ipython==8.4.0',
        'matplotlib==3.4.3',
        'numpy==1.20.3',
        'Pillow==9.1.1',
        'pvlib==0.9.1',
        'python_dateutil==2.8.2',
        'pytz==2021.3',
        'requests==2.26.0',
        'seaborn==0.11.2',
        'Shapely==1.8.2',
        'tqdm==4.62.3',
        'bifacial_radiance==0.4.1',#content changed!
        # 'pyqt5==5.12.3'
        # 'pyqtwebengine==5.12.1'
        'pvfactors==1.5.2'
        #und pvfactors - welche Version?  
    ],

    # Here are the keywords of my library.
    keywords='Bifacialsimu, bifacial simulation,  energy yield of bifacial PV systems, albedo',

    # here are the packages I want "build."
    packages=['BifacialSimu_src'],
    
    # I also have some package data, like photos and JSON files, so
    # I want to include those as well.
    include_package_data=True,
      
    classifiers=[
           # Here I'll specify the version of Python it uses.
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          
          # I can say what phase of development my library is in.
          'Development Status :: 1 - Alpha',
          ]
# ==================== ADDTIONAL PACKAGE INFO =================================
# 
#     # # here we specify any package data.
#     # package_data={
# 
#     #     # And include any files found subdirectory of the "td" package.
#     #     "td": ["app/*", "templates/*"],
# 
#     # },
# 
#     # I also have some package data, like photos and JSON files, so
#     # I want to include those as well.
#     include_package_data=True,
# 
#     # Here I can specify the python version necessary to run this library.
#     python_requires='>=3.7',
# 
#     # Additional classifiers that give some characteristics about the package.
#     # For a complete list go to https://pypi.org/classifiers/.
#     classifiers=[
# 
#         # I can say what phase of development my library is in.
#         'Development Status :: 3 - Alpha',
# 
#         # Here I'll add the audience this library is intended for.
#         'Intended Audience :: Developers',
#         'Intended Audience :: Science/Research',
#         'Intended Audience :: Financial and Insurance Industry',
# 
#         # Here I'll define the license that guides my library.
#         'License :: OSI Approved :: MIT License',
# 
#         # Here I'll note that package was written in English.
#         'Natural Language :: English',
# 
#         # Here I'll note that any operating system can use it.
#         'Operating System :: OS Independent',
# 
#         # Here I'll specify the version of Python it uses.
#         'Programming Language :: Python',
#         'Programming Language :: Python :: 3',
#         'Programming Language :: Python :: 3.8',
# 
#         # Here are the topics that my library covers.
#         'Topic :: Database',
#         'Topic :: Education',
#         'Topic :: Office/Business'
# 
#     ]
# =============================================================================
)