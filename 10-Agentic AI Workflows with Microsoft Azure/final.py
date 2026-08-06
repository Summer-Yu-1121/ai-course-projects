# <TODO: Step 3 - Imports>
# Complete the imports for all the necessary components from the semantic_kernel library.
import asyncio
import json
import logging
import os
import traceback

import pandas as pd
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    SequentialSelectionStrategy,
    TerminationStrategy,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import AuthorRole, ChatMessageContent
from semantic_kernel.functions import KernelArguments

# -----------------
# Logging Setup
# -----------------
# The logging setup below captures all agent interactions and saves them to 'logs/agent_chat.log'.
# 1. Create a dedicated logger for agent interactions.
agent_logger = logging.getLogger("semantic_kernel.agents")
agent_logger.setLevel(logging.DEBUG)

# 2. Prevent agent logs from propagating to other handlers (like console).
agent_logger.propagate = False

# 3. Create a file handler to write to 'agent_chat.log' in write mode.
agent_chat_handler = logging.FileHandler("logs/agent_chat.log", mode='w')
agent_chat_handler.setLevel(logging.DEBUG)

# 4. Create a minimal formatter to log only the message content.
chat_formatter = logging.Formatter('%(asctime)s - %(name)s:%(message)s')
agent_chat_handler.setFormatter(chat_formatter)

# 5. Add the dedicated file handler to the agent logger.
agent_logger.addHandler(agent_chat_handler)

# 6. Function to log agent messages
def log_agent_message(content):
    try:
        agent_logger.info(f"Agent: {content.role} - {content.name or '*'}: {content.content}")
    except Exception:
        agent_logger.exception("Failed to write agent message to log")

# -----------------
# Environment Setup
# -----------------
# <TODO: Step 2 - Environment Setup>
# Load the API key and endpoint URL from the .env file.

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

API_VERSION = "2024-05-01-preview"


# -----------------
# Kernel and Chat Service
# -----------------
# <TODO: Step 3 - Kernel Initialization>
# Initialize the Kernel, define the AzureChatCompletion service, and add it to the kernel.
kernel = Kernel()

chat_service = AzureChatCompletion(
    service_id="azure_openai",
    deployment_name=DEPLOYMENT_NAME,
    endpoint=BASE_URL,
    api_key=API_KEY,
    api_version=API_VERSION,
)

kernel.add_service(chat_service)


# -----------------
# Helper Functions
# -----------------
# <TODO: Step 4 - Implement Supporting Logic>
# Implement the logic for each of the helper functions below.

def load_quality_instructions(file_path):
    try:
        with open(
            os.path.join("specs", file_path),
            "r",
            encoding="utf-8"
        ) as file:
            return [
                line.strip()
                for line in file.readlines()
                if line.strip()
            ]
    except FileNotFoundError:
        print(f"Quality instructions file not found: {file_path}")
        return []


def load_reports_instructions(file_path):
    try:
        with open(
            os.path.join("specs", file_path),
            "r",
            encoding="utf-8"
        ) as file:
            return [
                line.strip()
                for line in file.readlines()
                if line.strip()
            ]
    except FileNotFoundError:
        print(f"Report instructions file not found: {file_path}")
        return []


def load_logs(file_path):
    try:
        with open(
            os.path.join("logs", file_path),
            "r",
            encoding="utf-8"
        ) as file:
            return file.readlines()

    except FileNotFoundError:
        print(f"Log file not found: {file_path}")
        return []


def get_csv_name():
    csv_files = [
        f for f in os.listdir("data")
        if f.endswith(".csv")
    ]

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data directory."
        )

    print("\nAvailable CSV Files:")

    for index, filename in enumerate(
        csv_files,
        start=1
    ):
        print(f"{index}. {filename}")

    selection = int(
        input("Select CSV file number: ")
    )

    return os.path.join(
        "data",
        csv_files[selection - 1]
    )


def load_csv_file(file_path):
    try:
        dataframe = pd.read_csv(file_path)

        flattened = dataframe.values.flatten().tolist()

        return ", ".join(
            map(str, flattened)
        )

    except Exception as error:
        print(f"Failed to load CSV: {error}")
        return ""


class PythonExecutor:
    """
    A safe executor for dynamically generated Python code strings.
    """

    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts

    def run(self, code):
        try:
            exec(code, {})
            return True, None

        except Exception:
            return (
                False,
                traceback.format_exc()
            )


def save_final_report(
    report,
    path="artifacts/final_report.md"
):
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)
# -----------------
# Agent Instructions
# -----------------
# <TODO: Step 5 - Build the Agents and Teams>
# 1. Complete the AGENT_CONFIG with detailed prompts for each agent.
data_quality_instructions = ''.join(load_quality_instructions("Data_Quality_Instructions.txt"))
report_instructions = ''.join(load_reports_instructions("Report_Instructions.txt"))

AGENT_CONFIG = {
    "PythonExecutorAgent": """
You are the PythonExecutorAgent.

Generate executable Python visualization code.

Requirements:
- Use pandas and matplotlib.
- Read the original CSV file.
- Read data-cleaned.json as a JSON array of record objects.
- Select an appropriate numeric column.
- Plot the original numeric data in blue.
- Plot the cleaned numeric data in green.
- Use a single line chart.
- Include a title, axis labels, and legend.
- Ensure the artifacts directory exists.
- Save the plot exactly as:
  artifacts/data_visualization.png
- Do not call plt.show().
- Return only raw executable Python code.
- Do not use markdown code fences.
- Do not include explanations outside the code.
""",

    "DataCleaning": """
You are the DataCleaning agent.

Your only responsibility is to clean the supplied dataset.

Tasks:
1. Parse the supplied CSV dataset.
2. Identify missing values.
3. Identify duplicate rows.
4. Identify inconsistent or malformed values.
5. Identify and remove obvious numerical outliers.
6. Remove or correct invalid records.

STRICT OUTPUT REQUIREMENTS:
- Return ONLY the final cleaned dataset.
- The output must be a valid JSON array of record objects.
- Every object must use the original CSV column names.
- Do not use markdown code fences.
- Do not include a cleaning plan.
- Do not include explanations.
- Do not calculate descriptive statistics.
- Do not validate the analysis.
- Do not approve the workflow.
- Do not use the word APPROVED.

Example output:
[
  {"Sensor Value": 0.12},
  {"Sensor Value": 0.83}
]
""",

"DataStatistics": """
You are the DataStatistics agent.

The preceding DataCleaning response contains the cleaned dataset
as a JSON array of record objects.

Your responsibilities:
1. Use only the cleaned dataset returned by DataCleaning.
2. Calculate the number of cleaned records.
3. Calculate minimum and maximum.
4. Calculate mean and median.
5. Calculate sample standard deviation.
6. Provide concise statistical observations.

Return exactly:

Count: <value>
Minimum: <value>
Maximum: <value>
Mean: <value>
Median: <value>
Sample Standard Deviation: <value>

Observations:
- <observation>

STRICT OUTPUT REQUIREMENTS:
- Do not clean the dataset again.
- Do not return another cleaned JSON dataset.
- Do not validate the workflow.
- Do not approve the workflow.
- Do not use the word APPROVED.
""",

"AnalysisChecker": f"""
You are the AnalysisChecker agent.

Review the immediately preceding DataCleaning and DataStatistics
responses.

The required separation of duties is intentional:

- DataCleaning must return ONLY a valid JSON array of cleaned records.
- DataCleaning must not return a cleaning plan, explanations,
  statistics, or approval.
- DataStatistics must calculate statistics separately.
- AnalysisChecker is responsible for validation and narration.

Validate all of the following:

1. DataCleaning returned a valid JSON array of record objects.
2. The cleaned records use the original CSV column names.
3. The cleaned dataset contains only valid cleaned records.
4. Obvious numerical outliers are absent from the cleaned dataset.
5. DataStatistics used all cleaned records exactly once.
6. Recalculate count, minimum, maximum, mean, median, and
   sample standard deviation from the cleaned dataset.
7. Confirm that the recalculated values agree with the
   DataStatistics response.
8. Do not fail the workflow because DataCleaning omitted a
   cleaning plan or explanations. JSON-only output is required.
9. Do not fail the workflow because DataStatistics includes
   one concise observations section.

Supporting data quality requirements:

{data_quality_instructions}

OUTPUT REQUIREMENTS:
- Provide a concise validation summary.
- Do not return a JSON object.
- Do not repeat the complete original or cleaned datasets.
- If any value or required condition is wrong, explain the issue
  and do not approve.
- If every requirement is satisfied, the final non-empty line
  must be exactly:

APPROVED
""",

    "ReportGenerator": f"""
You are the ReportGenerator agent.

Generate a complete markdown data analysis report using:
- the cleaning result,
- the statistical result,
- the validation result,
- the visualization information,
- the human approval,
- and the agent interaction log.

Follow these report instructions:
{report_instructions}

STRICT OUTPUT REQUIREMENTS:
- Generate the markdown report only.
- Do not validate the report.
- Do not approve the report.
- Do not use the word APPROVED.
""",

       "ReportChecker": f"""
You are the ReportChecker agent.

Review the preceding markdown report.

Validate the report against:
{report_instructions}

Check:
- required sections,
- factual consistency,
- cleaning description,
- statistical analysis,
- visualization reference,
- conclusions,
- and markdown formatting.

STRICT OUTPUT REQUIREMENTS:
- Explain any remaining correction before the verdict.
- If every requirement is satisfied, the final non-empty line
  must be exactly:
APPROVED
- If any requirement is not satisfied, do not output APPROVED.
"""
}
# -----------------
# Agent Factory
# -----------------
# <TODO: Step 5 - Build the Agents and Teams>
# 2. Implement the agent factory function.
def create_agent(name, instructions, service, settings=None):
    """Factory function to create a new ChatCompletionAgent."""

    arguments = None

    if settings:
        arguments = KernelArguments(
            settings=settings
        )

    return ChatCompletionAgent(
        name=name,
        instructions=instructions,
        kernel=kernel,
        arguments=arguments,
    )

# -----------------
# Termination Strategy
# -----------------
# A custom termination strategy that stops after user approval.
class ApprovalTerminationStrategy(TerminationStrategy):
    """
    Terminate only when an authorized checker ends its response
    with the exact final token APPROVED.
    """

    async def should_agent_terminate(self, agent, history):
        agent_name = getattr(agent, "name", None)

        print(
            "TERMINATION CHECK:",
            repr(agent_name),
            type(agent).__name__,
        )

        if not history:
            print("TERMINATION RESULT: False, empty history")
            return False

        content = str(history[-1].content or "").strip()

        non_empty_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not non_empty_lines:
            print("TERMINATION RESULT: False, empty response")
            return False

        final_line = non_empty_lines[-1]

        normalized_final_line = (
            final_line
            .replace("*", "")
            .replace("`", "")
            .strip()
            .upper()
        )

        should_stop = normalized_final_line == "APPROVED"

        print(
            "TERMINATION AGENT:",
            repr(agent_name),
        )
        print(
            "TERMINATION FINAL LINE:",
            repr(normalized_final_line),
        )
        print(
            "TERMINATION RESULT:",
            should_stop,
        )

        return should_stop

# -----------------
# Agent Instantiation
# -----------------
# <TODO: Step 5 - Build the Agents and Teams>
# 3. Instantiate each agent with the correct name, prompt, and temperature setting.
python_agent = create_agent(
    name="PythonExecutorAgent",
    instructions=AGENT_CONFIG["PythonExecutorAgent"],
    service=chat_service,
    settings=OpenAIChatPromptExecutionSettings(
        service_id="azure_openai",
        temperature=0.1,
    ),
)

cleaning_agent = create_agent(
    name="DataCleaning",
    instructions=AGENT_CONFIG["DataCleaning"],
    service=chat_service,
    settings=OpenAIChatPromptExecutionSettings(
        service_id="azure_openai",
        temperature=0.7,
    ),
)

stats_agent = create_agent(
    name="DataStatistics",
    instructions=AGENT_CONFIG["DataStatistics"],
    service=chat_service,
    settings=OpenAIChatPromptExecutionSettings(
        service_id="azure_openai",
        temperature=0.5,
    ),
)

checker_agent = create_agent(
    name="AnalysisChecker",
    instructions=AGENT_CONFIG["AnalysisChecker"],
    service=chat_service,
    settings=OpenAIChatPromptExecutionSettings(
        service_id="azure_openai",
        temperature=0.2,
    ),
)

report_agent = create_agent(
    name="ReportGenerator",
    instructions=AGENT_CONFIG["ReportGenerator"],
    service=chat_service,
    settings=OpenAIChatPromptExecutionSettings(
        service_id="azure_openai",
        temperature=1.0,
    ),
)

report_checker_agent = create_agent(
    name="ReportChecker",
    instructions=AGENT_CONFIG["ReportChecker"],
    service=chat_service,
    settings=OpenAIChatPromptExecutionSettings(
        service_id="azure_openai",
        temperature=0.2,
    ),
)
# -----------------
# Group Chats
# -----------------
# <TODO: Step 5 - Build the Agents and Teams>
# 4. Create the three agent group chats.

analysis_chat = AgentGroupChat(
    agents=[
        cleaning_agent,
        stats_agent,
        checker_agent,
    ],
    selection_strategy=SequentialSelectionStrategy(
        initial_agent=cleaning_agent
    ),
    termination_strategy=ApprovalTerminationStrategy(
        agents=[
            checker_agent,
        ],
        maximum_iterations=3,
    ),
)

code_chat = AgentGroupChat(
    agents=[
        python_agent,
    ]
)

report_chat = AgentGroupChat(
    agents=[
        report_agent,
        report_checker_agent,
    ],
    selection_strategy=SequentialSelectionStrategy(
        initial_agent=report_agent
    ),
    termination_strategy=ApprovalTerminationStrategy(
        agents=[
            report_checker_agent,
        ],
        maximum_iterations=2,
    ),
)

# -----------------
# Main Workflow
# -----------------
# <TODO: Step 6 - Orchestrate the Main Workflow>
# Implement the main workflow logic, following the sequence described in the instructions.
async def main():
    """Run the complete AI-powered data analysis workflow."""

    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    def get_message_text(message):
        """Convert a Semantic Kernel response to plain text."""
        return str(message.content or "").strip()

    def clean_python_code(code):
        """Remove markdown fences from generated Python code."""
        code = code.strip()

        if code.startswith("```python"):
            code = code[len("```python"):].strip()
        elif code.startswith("```"):
            code = code[3:].strip()

        if code.endswith("```"):
            code = code[:-3].strip()

        return code

    def reset_chat(chat):
        """Reset completion status before reusing a chat."""
        if getattr(chat, "is_complete", False):
            chat.is_complete = False

    try:
        print("\n=== AI Data Analysis Workflow ===")

        # -------------------------------------------------
        # 1. Load the CSV data
        # -------------------------------------------------
        csv_path = get_csv_name()
        original_df = pd.read_csv(csv_path)

        if original_df.empty:
            print("The selected CSV file is empty.")
            return

        original_csv_text = original_df.to_csv(index=False)

        print(f"\nSelected file: {csv_path}")
        print(f"Rows: {len(original_df)}")
        print(f"Columns: {len(original_df.columns)}")

        # -------------------------------------------------
        # 2. Invoke the analysis chat
        # -------------------------------------------------
        reset_chat(analysis_chat)

        analysis_prompt = f"""
Analyze the following CSV dataset.

Source file:
{csv_path}

CSV data:
{original_csv_text}

Required sequence:

1. DataCleaning:
   - Clean the dataset.
   - Identify missing values.
   - Identify duplicate rows.
   - Identify inconsistent values.
   - Identify obvious numerical outliers.
   - Return ONLY a valid JSON array.
   - Do not return explanations.
   - Do not return statistics.
   - Do not approve the workflow.

2. DataStatistics:
   - Use only the cleaned JSON array.
   - Calculate count, minimum, maximum,
     mean, median and sample standard deviation.
   - Provide concise observations.
   - Do not clean data again.
   - Do not approve the workflow.

3. AnalysisChecker:
   - Validate the cleaning result.
   - Validate the statistics.
   - Confirm compliance with Data_Quality_Instructions.txt.
   - If everything is correct, the final non-empty line
     must be exactly:

APPROVED
"""

        await analysis_chat.add_chat_message(
            ChatMessageContent(
                role=AuthorRole.USER,
                content=analysis_prompt,
            )
        )

        cleaning_output = ""
        statistics_output = ""
        validation_output = ""

        print("\n=== Analysis Phase ===")

        async for response in analysis_chat.invoke():
            log_agent_message(response)

            response_name = response.name or "UnknownAgent"
            response_text = get_message_text(response)

            print(f"\n[{response_name}]")
            print(response_text)

            if response_name == "DataCleaning":
                cleaning_output = response_text

            elif response_name == "DataStatistics":
                statistics_output = response_text

            elif response_name == "AnalysisChecker":
                validation_output = response_text

        if not cleaning_output:
            print("DataCleaning did not return a result.")
            return
        validation_lines = [
            line.strip()
            for line in validation_output.splitlines()
            if line.strip()
        ]

        validation_approved = (
            bool(validation_lines)
            and validation_lines[-1]
            .replace("*", "")
            .replace("`", "")
            .strip()
            .upper()
            == "APPROVED"
        )

        if not validation_approved:
            print(
                "\nAnalysisChecker did not approve the analysis. "
                "Workflow stopped before human approval."
            )
            return
        # -------------------------------------------------
        # 3. Human approval
        # -------------------------------------------------
        print("\n=== Human Approval Checkpoint ===")

        print("\nCleaning output:")
        print(cleaning_output)

        if statistics_output:
            print("\nStatistics output:")
            print(statistics_output)

        if validation_output:
            print("\nValidation output:")
            print(validation_output)

        approval = input(
            "\nDo you approve the cleaned data and analysis? "
            "Enter yes to continue: "
        ).strip().lower()

        agent_logger.info(
            "Human approval status: %s",
            approval,
        )

        if approval != "yes":
            print("Workflow stopped because approval was not granted.")
            return

               # -------------------------------------------------
        # 4. Save the cleaned data
        # -------------------------------------------------
        cleaned_text = cleaning_output.strip()

        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[
                len("```json"):
            ].strip()
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:].strip()

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()

        try:
            cleaned_data = json.loads(cleaned_text)

        except json.JSONDecodeError as error:
            raise ValueError(
                "DataCleaning did not return valid JSON. "
                f"{error}"
            ) from error

        if not isinstance(cleaned_data, list):
            raise ValueError(
                "The cleaned dataset must be a JSON array."
            )

        if not cleaned_data:
            raise ValueError(
                "The cleaned dataset is empty."
            )

        if not all(
            isinstance(record, dict)
            for record in cleaned_data
        ):
            raise ValueError(
                "Every cleaned item must be a JSON object."
            )

        original_columns = set(
            original_df.columns
        )

        for record in cleaned_data:
            if set(record.keys()) != original_columns:
                raise ValueError(
                    "Column mismatch in cleaned data."
                )

        with open(
            "data-cleaned.json",
            "w",
            encoding="utf-8",
        ) as cleaned_file:
            json.dump(
                cleaned_data,
                cleaned_file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        print(
            f"\nSaved {len(cleaned_data)} cleaned records: "
            "data-cleaned.json"
        )
        # -------------------------------------------------
        # 5. Generate visualization code
        # -------------------------------------------------
        reset_chat(code_chat)

        visualization_prompt = f"""
Generate executable Python visualization code.

Input files:
- Original CSV: {csv_path}
- Cleaned JSON: data-cleaned.json

Requirements:
- Use pandas and matplotlib.
- Ensure the artifacts directory exists.
- Read the original CSV and cleaned JSON.
- Select appropriate numerical data.
- Plot original data in blue.
- Plot cleaned data in green.
- Display both series in one line chart.
- Include title, axis labels, and legend.
- Save the plot exactly as:
  artifacts/data_visualization.png
- Do not call plt.show().
- Return only raw executable Python code.
- Do not use markdown code fences.
- Do not include an explanation.
"""

        await code_chat.add_chat_message(
            ChatMessageContent(
                role=AuthorRole.USER,
                content=visualization_prompt,
            )
        )

        generated_code = ""

        print("\n=== Code Generation Phase ===")

        async for response in code_chat.invoke(
            agent=python_agent
        ):
            log_agent_message(response)
            generated_code = get_message_text(response)

            print(
                f"\n[{response.name or 'PythonExecutorAgent'}]"
            )
            print(generated_code)

        if not generated_code:
            print("PythonExecutorAgent returned no code.")
            return

        working_code = clean_python_code(generated_code)

        # -------------------------------------------------
        # 6. Execute code with retries
        # -------------------------------------------------
        executor = PythonExecutor(max_attempts=10)
        execution_successful = False
        execution_error = None

        for attempt in range(
            1,
            executor.max_attempts + 1
        ):
            print(
                f"\nExecution attempt "
                f"{attempt}/{executor.max_attempts}"
            )

            execution_successful, execution_error = (
                executor.run(working_code)
            )

            plot_exists = os.path.exists(
                "artifacts/data_visualization.png"
            )

            if execution_successful and plot_exists:
                print("Visualization generated successfully.")
                break

            if execution_successful and not plot_exists:
                execution_error = (
                    "The Python code ran without an exception, "
                    "but artifacts/data_visualization.png "
                    "was not created."
                )

            print("\nExecution failed:")
            print(execution_error)

            if attempt == executor.max_attempts:
                break

            reset_chat(code_chat)

            correction_prompt = f"""
Correct the visualization code.

Previous code:
{working_code}

Execution error:
{execution_error}

Requirements:
- Use pandas and matplotlib.
- Plot original data in blue.
- Plot cleaned data in green.
- Use one line chart.
- Save exactly as:
  artifacts/data_visualization.png
- Return only corrected raw Python code.
- Do not use markdown fences.
"""

            await code_chat.add_chat_message(
                ChatMessageContent(
                    role=AuthorRole.USER,
                    content=correction_prompt,
                )
            )

            corrected_code = ""

            async for response in code_chat.invoke(
                agent=python_agent
            ):
                log_agent_message(response)
                corrected_code = get_message_text(response)

            if corrected_code:
                working_code = clean_python_code(
                    corrected_code
                )

        if (
            not execution_successful
            or not os.path.exists(
                "artifacts/data_visualization.png"
            )
        ):
            print(
                "Visualization failed after all retry attempts."
            )
            return

        # -------------------------------------------------
        # 7. Save the working Python code
        # -------------------------------------------------
        with open(
            "artifacts/data_visualization_code.py",
            "w",
            encoding="utf-8",
        ) as code_file:
            code_file.write(working_code)

        print(
            "Saved: artifacts/data_visualization_code.py"
        )
        print(
            "Saved: artifacts/data_visualization.png"
        )

        for handler in agent_logger.handlers:
            handler.flush()

        # -------------------------------------------------
        # 8. Generate the report from logs
        # -------------------------------------------------
        log_entries = load_logs("agent_chat.log")
        log_text = "".join(log_entries)

        reset_chat(report_chat)

        report_prompt = f"""
Generate a complete structured markdown report.

Source CSV:
{csv_path}

Cleaned data:
data-cleaned.json

Visualization code:
artifacts/data_visualization_code.py

Visualization image:
artifacts/data_visualization.png

Cleaning output:
{cleaning_output}

Statistics:
{statistics_output}

Analysis validation:
{validation_output}

Human approval:
yes

Agent interaction log:
{log_text}

Follow Report_Instructions.txt exactly.

ReportGenerator must create the complete report.
ReportChecker must verify completeness, accuracy,
formatting, and all required sections.
ReportChecker must include APPROVED only when the
report satisfies every requirement.
"""

        await report_chat.add_chat_message(
            ChatMessageContent(
                role=AuthorRole.USER,
                content=report_prompt,
            )
        )

        generated_report = ""
        report_validation = ""

        print("\n=== Report Phase ===")

        async for response in report_chat.invoke():
            log_agent_message(response)

            response_name = response.name or "UnknownAgent"
            response_text = get_message_text(response)

            print(f"\n[{response_name}]")
            print(response_text)

            if response_name == "ReportGenerator":
                generated_report = response_text

            elif response_name == "ReportChecker":
                report_validation = response_text

        if not generated_report:
            print("ReportGenerator returned no report.")
            return

        # -------------------------------------------------
        # 9. Save the final report
        # -------------------------------------------------
        save_final_report(
            generated_report,
            "artifacts/final_report.md",
        )

        print("\nSaved: artifacts/final_report.md")

        if report_validation:
            print("\nReport validation:")
            print(report_validation)

        # -------------------------------------------------
        # Final output validation
        # -------------------------------------------------
        required_files = [
            "data-cleaned.json",
            "artifacts/data_visualization_code.py",
            "artifacts/data_visualization.png",
            "artifacts/final_report.md",
        ]

        print("\n=== Final File Check ===")

        all_files_exist = True

        for required_file in required_files:
            if os.path.exists(required_file):
                print(f"[OK] {required_file}")
            else:
                print(f"[MISSING] {required_file}")
                all_files_exist = False

        if all_files_exist:
            print(
                "\nWorkflow completed successfully. "
                "All required files were created."
            )
        else:
            print(
                "\nWorkflow finished, but required files "
                "are missing."
            )

    except KeyboardInterrupt:
        print("\nWorkflow stopped by the user.")

    except Exception as error:
        agent_logger.exception(
            "Unexpected workflow error"
        )

        print("\nWorkflow failed:")
        print(error)
        print(traceback.format_exc())
# -----------------
# Main Execution
# -----------------
if __name__ == "__main__":
    asyncio.run(main())