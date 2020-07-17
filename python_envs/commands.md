
Create an environmemt

```bash
conda env create -f "E:\tuxedo\Github\Tools_and_Scripts\python_envs\conda_env_imageanalysis_win10.yml"
```

Update an environment

```bash
conda env update --prefix ./env --file "E:\tuxedo\Github\Tools_and_Scripts\python_envs\conda_env_imageanalysis_win10.yml"  --prune
```
Remove an environment

```bash
conda remove --name imageanalysis_win10 --all
```
