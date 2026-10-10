FROM mysql:8.4

# Windows 에서 설정 파일을 볼륨으로 마운트하면 권한이 777 로 보여
# "World-writable config file ... is ignored" 경고와 함께 설정이 무시된다.
# 그래서 마운트하지 않고 권한 644 로 이미지에 복사한다.
COPY --chmod=644 conf.d/my.cnf /etc/mysql/conf.d/my.cnf
