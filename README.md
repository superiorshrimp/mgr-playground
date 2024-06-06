# mgr-playground

### Instalacja

```
pip install "ray[default]"
pip install jmetalpy
pip install scikit-learn

ray start --head --port=6379 --dashboard-port=6380

python islands_desync\minimal.py 3 8 8

ray stop
```
