from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [], include_msvcr =[True])

base = 'Console'

executables = [
    Executable('lazyloader.py', base=base)
]

setup(name='lazyloader',
      version = '1.0',
      description = 'Automatically creates your own personal autoloader',
      options = dict(build_exe = buildOptions),
      executables = executables)

#TO BUILD:
#>python setup.py build_exe
