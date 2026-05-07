# 🚀 Module 2: Advanced RAG Patterns with LangGraph

Welcome to Module 2 of the Workshop series! In this module, you'll learn how to orchestrate LLMs through graph patterns.

## 🎯 What You'll Learn

In this hands-on workshop, you'll:

- 🛠️ Set up a RAG environment with ChromaDB
- 🔄 Create workflow graphs with LangGraph
- 📝 Implement effective prompt chaining patterns
- 🧠 Build intelligent query routing systems
- 📊 Utilize parallel processing for efficiency
- 🔍 Create orchestrator-worker patterns for complex tasks
- 🧩 Implement evaluator-optimizer patterns for continuous improvement

## 📋 Prerequisites

We highly recommend you start at module 1. Setup instructions can be found in the main readme.

## 📚 Workshop Notebooks

The workshop consists of 6 notebooks that build upon each other:

### 1. Setup and Basics (`1_setup.ipynb`)

- 🔧 Setting up the environment
- 💾 Creating ChromaDB vector store
- 🚀 Downloading and processing data

### 2. Prompt Chaining (`2_prompt_chaining.ipynb`)

- 📊 Breaking down complex tasks
- 🔄 Implementing sequential processing
- 💾 Building clear information flows

### 3. Routing (`3_routing.ipynb`)

- 🧠 Creating intelligent classifiers
- 🔀 Implementing specialized handlers
- 📈 Building dynamic routing logic

### 4. Parallelization (`4_parallelization.ipynb`)

- 🚀 Running multiple tasks simultaneously
- ⚡ Implementing async processing
- 📊 Optimizing resource usage

### 5. Orchestrator Pattern (`5_orchestrator.ipynb`)

- 🎮 Coordinating complex workflows
- 🧩 Implementing dynamic task execution
- 🔍 Building flexible diagnostic systems

### 6. Evaluator-Optimizer Pattern (`6_evaluator_optimizer.ipynb`)

- 📈 Implementing answer improvement systems
- ✅ Creating quality evaluation logic
- 🔄 Building iterative refinement loops

## 🧭 Workshop Flow

1. Start with the setup notebook to build your vector store
2. Follow the notebooks in numerical order
3. Complete the exercises in each notebook
4. Review the example solutions provided

Each notebook includes:

- Clear explanations of concepts
- Step-by-step instructions
- Code examples you can run
- Practice exercises to reinforce learning

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### Authentication Error

- Check AWS credentials are properly configured
- Verify IAM role has bedrock:InvokeModel permission
- Ensure region matches your Bedrock endpoint

#### ChromaDB Issues

- Verify data directory exists
- Check disk space availability
- Ensure proper permissions for the directory

#### LangGraph Workflow Error

- Ensure all node functions have correct signatures
- Verify state model matches workflow requirements
- Check for proper type hints

#### Memory Issues

- Reduce batch sizes in parallel processing
- Implement pagination for large document sets
- Consider using a larger instance if in a cloud environment

#### Type Validation Error

- Check input data matches Pydantic models
- Verify all required fields are provided
- Ensure proper type conversions

## 🆘 Getting Help

If you encounter issues:

1. Check your AWS credentials and permissions
2. Verify Bedrock model access (especially for Claude models)
3. Ensure all required packages are installed via `uv sync`
4. Review error messages carefully

Start with `1_setup.ipynb` and proceed through each notebook in sequence. Each builds upon the concepts learned in the previous notebooks.

Happy learning! 🎉
