---
marp: true
theme: dark-plus-code
paginate: true
style: |

---

# Jupyter Lab 설정 파일에 옵션을 저장해서 실행하기

## : 설정 파일 생성 

```bash
jupyter lab --generate-config
```
- `~/.jupyter/jupyter_lab_config.py` 에 `jupyter_lab_config.py` 생성

**2) 파일 열어서 옵션 추가**
```bash
notepad ~/.jupyter/jupyter_lab_config.py
# 또는
code ~/.jupyter/jupyter_lab_config.py
```
- 아래 줄을 파일 어딘가(또는 맨 아래)에 추가:
```python
c.ContentsManager.allow_hidden = True
```
