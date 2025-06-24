#!/usr/bin/env python3
import os
import subprocess
import sys
import yaml
import click

@click.command()
@click.option('--config', '-c', default='config.yaml',
              help='Path to the YAML config file')
def main(config):
    """
    1. Loads a YAML file listing GitHub repositories and shell commands.
    2. Clones or pulls each repo.
    3. Executes each listed command.
    """
    # Load config
    try:
        with open(config) as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Config file not found: {config}")
        sys.exit(1)

    repos = cfg.get('repos', [])
    commands = cfg.get('commands', [])

    # Clone or update repos
    for repo in repos:
        url = repo['url']
        dest = repo.get('dest', os.path.basename(url).replace('.git', ''))
        if not os.path.isdir(dest):
            click.echo(f"Cloning {url} into {dest}...")
            subprocess.run(['git', 'clone', url, dest], check=True)
        else:
            click.echo(f"Updating existing repo at {dest}...")
            subprocess.run(['git', '-C', dest, 'pull'], check=True)

    # Run arbitrary commands
    for cmd in commands:
        click.echo(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            click.echo(f"Command failed (exit {result.returncode}): {cmd}")
            sys.exit(result.returncode)

    click.echo("✅ All tasks completed successfully.")

if __name__ == '__main__':
    main()