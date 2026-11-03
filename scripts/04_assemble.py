# Rebuild index.html from the template and the data produced by 03_build_data.py
import pathlib
here=pathlib.Path(__file__).parent
t=(here/"app_template.html").read_text(encoding="utf-8")
d=(here/"data.json").read_text(); b=(here/"blob.b64").read_text()
(here.parent/"index.html").write_text(t.replace("__DATA__",d).replace("__BLOB__",b),encoding="utf-8")
print("index.html rebuilt")
