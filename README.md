# TemplateRepo

[![Awesome](https://awesome.re/badge.svg)](https://github.com/Chip-Security-Lab/TemplateRepo) 
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview
[VerilogCoder](https://arxiv.org/abs/2408.08927) is a RTL generation framework LLM-based.

## 🔔 News
- **New Reports**

- **2024-07-22 We release a new paper: "[Paper Name](https://arxiv.org/abs/2407.15017)", which reviews how knowledge is acquired, utilized, and evolves in large language models.**
- **2023-05  We release a new analysis paper:"[Paper Name](https://arxiv.org/abs/2305.13172)" based on this repository! We are looking forward to any comments or discussions on this topic :)**
- **2022-12 We create this repository to maintain a template repository.**

(更新信息，如新论文、新数据集、新工具等)

---

## 🔍 Contents

- [TemplateRepo](#templaterepo)
  - [📖 Overview](#-overview)
  - [🔔 News](#-news)
  - [🔍 Contents](#-contents)
  - [🌏 Environment](#-environment)
  - [🔧 Usage](#-usage)
  - [📌 Citation](#-citation)
    - [BibTex](#bibtex)
  - [🎉Contribution](#contribution)
    - [Contributors](#contributors)

---

## 🌏 Environment

(列出代码运行环境，如操作系统、依赖库等)

In order to use PyHDL-Eval you will need to install iverilog, verilator,
and python3 along with several Python packages. These are the versions
which were used for this project:

 - iverilog (v12)
 - python3 (v3.11.0)


To install Python 3.11:
```
$ conda create -n codex python=3.11
$ conda activate codex
```

Install [ICARUS Verilog](https://github.com/steveicarus/iverilog):
```
$ git clone https://github.com/steveicarus/iverilog.git && cd iverilog \
        && git checkout v12-branch \
        && sh ./autoconf.sh && ./configure && make -j4\
        && make install
```

You will also need the following Python packages:

```
 % pip install langchain langchain-openai langchain-nvidia-ai-endpoints
```

We plan to provide a Dockerfile and backwards compatibility mode with a prebuilt jsonl soon.

---

## 🔧 Usage

(给出使用说明，如如何安装依赖、如何运行代码等；以及代码结构、代码文件说明等)

The evalution harness is run using make and various evaluation parameters can be set as below:

```
mkdir -p build/
../configure  --with-task=$task --with-model=$model --with-examples=$shots --with-samples=$samples --with-temperature=$temperature --with-top-p=$top_p
make
```

Evaluation can be sped up by providing the `-j` flag to make, such as `-j4` to run 4 worker processes.

Available tasks are `code-complete-iccad2023` and `spec-to-rtl` with each referencing their corresponding `dataset_$task` directory containig the problems. Problem themselves are identical between the two datasets and only the task format changes.

Valid models are listed at the top of `scripts/sv-generate`. The number of in-context learning examples can be between 0-4, and given with `--with-examples`. Samples to collect per problem are given by `--with-samples`. Finally, model temperature and top_p can be set to --with-temperature and --with-top-p, respectively.

These parameters can be easily swept with a shell script, to create separate build directories for each evaluation harness configuration target. 

---

## 📌 Citation

Please cite our paper if find our work useful.

### BibTex
```
@misc{ho2024verilogcoderautonomousverilogcoding,
      title={VerilogCoder: Autonomous Verilog Coding Agents with Graph-based Planning and Abstract Syntax Tree (AST)-based Waveform Tracing Tool}, 
      author={Chia-Tung Ho and Haoxing Ren and Brucek Khailany},
      year={2024},
      eprint={2408.08927},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2408.08927}, 
}
```
## 🎉Contribution
### Contributors

<a href="https://github.com/Chip-Security-Lab/TemplateRepo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Chip-Security-Lab/TemplateRepo" />
</a>