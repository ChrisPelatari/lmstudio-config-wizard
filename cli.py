import argparse
import os
import yaml
import questionary
from hardware_utils import get_hardware_profile
from model_profile import ask_model_profile
from recommender import recommend_settings
from lms_client import test_config
from rich import print
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from rich.console import Console


def display_config(config):
    table = Table(title="Recommended LM Studio Configuration", title_style="bold cyan")
    table.add_column("Parameter", style="bold magenta")
    table.add_column("Value", style="green")

    for key, value in config.items():
        table.add_row(key, str(value))

    console = Console()
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="LM Studio Config Recommender")
    parser.add_argument(
        "--export", type=str, help="Export the recommended config to a YAML file"
    )
    args = parser.parse_args()

    print("\n[bold green]🔍 Detecting system hardware...[/bold green]")
    hardware_info = get_hardware_profile()

    # Display hardware details before asking questions
    print("\n[bold green]🧠 System Hardware Info[/bold green]")
    console = Console()
    table = Table(title="🧠 System Hardware Info", title_style="bold cyan")
    table.add_column("Component", style="bold magenta")
    table.add_column("Details", style="green")

    for key, value in hardware_info.items():
        table.add_row(key, str(value))

    console.print(table)

    print("\n[bold green]🧠 Understanding your model usage needs...[/bold green]")
    user_needs = ask_model_profile()

    print("\n[bold green]⚙️ Generating optimal configuration...[/bold green]")
    recommended_config = recommend_settings(hardware_info, user_needs)

    display_config(recommended_config)

    if questionary.confirm("🧪 Test these settings against LM Studio now?", default=False).ask():
        prompt = questionary.text(
            "💬 Enter a test prompt:",
            default="In one sentence, what is the capital of France?",
        ).ask()
        print("\n[bold yellow]⏳ Sending to LM Studio...[/bold yellow]")
        response = test_config(user_needs["model_name"], recommended_config, prompt)
        console = Console()
        console.print(Panel(response, title="[bold cyan]Model Response[/bold cyan]", expand=False))

    if args.export:
        model_name = user_needs.get("model_name", "default_model")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{model_name}_{timestamp}.yaml"
        output_path = os.path.join(os.path.dirname(args.export), output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            yaml.dump(recommended_config, f, allow_unicode=True)

        print(f"\n[green]✅ Configuration exported to:[/green] {output_path}\n")


if __name__ == "__main__":
    main()
