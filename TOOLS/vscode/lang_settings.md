---
marp: true
theme: dark-plus-code
paginate: true
style: |
  

---


# VSCode programming 환경 설정


--------------------

## C/C++ 설정

**gcc/g++ 컴파일러 설치**
- [mingw-64](https://www.mingw-w64.org/downloads/)
  - [Standalone mingw-w64+GCC builds for Windows](https://winlibs.com/)
  - 추천 버전: **GCC 13.2.0**


**필수 확장 설치**

- VSCode 확장에서 다음을 설치
- **`C/C++ Extension Pack (Microsoft)`** - IntelliSense, 디버깅, 컴파일 지원

-----------------------

**PATH 환경변수 설정**

> Windows 환경 변수에 추가하면 터미널에서 직접 g++/gcc를 사용할 수 있다:

- 제어판 → 시스템 → 고급 시스템 설정
- 환경 변수 → Path 편집
- C:\mingw64\bin 추가 후 저장
- VSCode 재시작

-----------------------
**작업 공간 폴더 구조**

- 프로젝트 폴더에 `.vscode` 폴더 생성
- 아래와 같은 파일을 생성한다.

```
your_project/
├── .vscode/
│   ├── tasks.json
│   ├── launch.json
│   └── c_cpp_properties.json
├── main.c (또는 main.cpp)
└── ...
```

----------------------
**`.vscode/tasks.json`** 작성

<div class="cols">
<div>

```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "build",
            "type": "shell",
            "command": "C:\\mingw64\\bin\\g++.exe",
            "args": [
                "-g",
                "${file}",
                "-o",
                "${fileDirname}\\${fileBasenameNoExtension}.exe"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
```

</div>
<div>

- `problemMatcher`을 왼쪽의 "group" 과 일치

```
            "problemMatcher": ["$gcc"],
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

</div>
</div>


----------------------

**`.vscode/launch.json` 작성


<div class="cols">
<div>

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "g++.exe - Debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "${fileDirname}\\${fileBasenameNoExtension}.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${fileDirname}",
            "environment": [],
            "externalConsole": true,            
```

</div>
<div>



```
            "MIMode": "gdb",
            "miDebuggerPath": "C:\\mingw64\\bin\\gdb.exe",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "build"
        }
    ]
}
```

</div>
</div>

---------------------

**`.vscode/c_cpp_properties.json`**



<div class="cols">
<div>

```
{
    "configurations": [
        {
            "name": "Win32",
            "includePath": [
                "${workspaceFolder}/**",
                "C:/mingw64/include",
                "C:/mingw64/lib/gcc/x86_64-w64-mingw32/13.2.0/include"
            ],
            "defines": [
                "_DEBUG",
                "UNICODE",
                "_UNICODE"
            ],
            "compilerPath": "C:\\mingw64\\bin\\g++.exe",
```

</div>
<div>



```
            "cStandard": "c17",
            "cppStandard": "c++20",
            "intelliSenseMode": "gcc-x64",
            "browse": {
                "path": [
                    "${workspaceFolder}",
                    "C:/mingw64"
                ],
                "limitSymbolsToIncludedHeaders": true,
                "databaseFilename": ""
            }
        }
    ],
    "version": 4
}         
```

</div>
</div>

---------------------

**빌드/디버깅 실행**

- 컴파일: `Ctrl`+`Shift`+`B`
- 디버깅 실행: `F5`
- 터미널에서 직접: `g++ -g main.c -o main.exe` (PATH 설정 후)

----------------------

## Java 설정

### 1단계: 시스템 환경 변수 설정

> `JAVA_HOME`과 `PATH` 환경 변수 설정:
> - `JAVA_HOME`: **C:\Program Files\Zulu\zulu-8**
> - `PATH`: **C:\Program Files\Zulu\zulu-8\bin** 추가


**확인**
```
javac -version
java -version
```

-------------------------

### 2단계: VSCode 확장 설치

- Extension Pack for Java 설치
  - "Extension Pack for Java" 검색 후 설치
  - Debugger for Java, Test Runner for Java 등이 함께 설치

- VSCode 설정 확인
  - 설정(`Ctrl+,`)에서 `java.home` 검색
  - 다음 값으로 설정:
   ` C:\Program Files\Zulu\zulu-8`


-----------------------

**설정 항목:**

- `.vscode/settings.json` - 컴파일러 경로 및 Java 홈 자동 설정
- `.vscode/tasks.json` - C/C++과 Java 빌드 작업 통합 설정
- `.vscode/launch.json` - C/C++과 Java 디버그 구성 설정
- VSCode 확장 추천 파일 (`extensions.json`) 생성

> Calude에게 작성 요청하기
