
<div align="center">
<img src="https://user-images.githubusercontent.com/1913203/215260281-edf84b41-6622-4a88-8b44-1e04085e4404.png"/>
<h1>YaYtD</h1>
<h5>Yet Another YouTube Downloader</h5>
<img src="https://user-images.githubusercontent.com/1913203/215263940-ddc129bf-a363-4549-921d-6f3177e0374f.png"/>
</div>

# What
YaYtD is a simple GUI built on top of [pytube](https://github.com/pytube/pytube) with [guizero](https://lawsie.github.io/guizero/) and a bit of [tkinter](https://docs.python.org/3/library/tkinter.html#module-tkinter) where necessary.

It lets you find all the streams associated with a YouTube video (audio only, video only or both combined) and download them to your machine for your convenience.
# Did we really need another one?
Probably not. But it seemed the perfect toy-project to learn about guizero, additionally, as an occasional user of the pytube cli I wondered how a handy GUI would have looked like.
# Install
Head to the releases and download your prebuilt flavor (Linux, Mac, Windows)

Or clone this repo and do:
```console
python -m venv env
source env/bin/activate
```
to create a python virtual environment in which to pip install the required modules:
```console
pip install -r requiremnts.txt
```
now you can either run yaytd with
```console
python yaytd.py
```
or build a single file executable for you platform with:
```console
pyinstaller -F yaytd.py
```
which should appear shortly after in the `dist` folder.
