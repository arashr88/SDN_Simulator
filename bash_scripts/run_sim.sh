#!/bin/bash

#SBATCH -p arm-preempt
#SBATCH -c 20
#SBATCH -G 0
#SBATCH --mem=40000
#SBATCH -t 4-00:00:00
#SBATCH -o slurm-%A_%a.out  # Output file for each task
#SBATCH --array=0-7  # Define array size based on total combinations

set -e  # Stop the script if any command fails

echo "Starting job with SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"

# Load Conda module
module load conda/latest

# Initialize Conda to enable 'conda activate'
eval "$(conda shell.bash hook)"

# Set a temporary Conda cache directory to avoid stale file issues
export CONDA_PKGS_DIRS="/tmp/conda_pkgs_$SLURM_ARRAY_TASK_ID"

# Define a unique environment name for each task
env_name="py311_env_${SLURM_ARRAY_TASK_ID}"

# Create a new Conda environment with Python 3.11.7 for this task
echo "Creating Conda environment $env_name"
conda create -n "$env_name" python=3.11.7 -y

# Activate the Conda environment for this task
conda activate "$env_name"

# Install required libraries from requirements.txt
pip install --cache-dir ~/.pip-cache -r ~/Git/SDON_simulator/requirements.txt

# Define parameter arrays
allocation_methods=("first_fit" "last_fit")
spectrum_allocation_priorities=("CSB" "BSC")
cores_per_link=(13 19)

# Calculate total combinations
total_combinations=$(( ${#allocation_methods[@]} * ${#spectrum_allocation_priorities[@]} * ${#cores_per_link[@]} ))

# Ensure the task ID is within the range of total combinations
if [ "$SLURM_ARRAY_TASK_ID" -ge "$total_combinations" ]; then
  echo "SLURM_ARRAY_TASK_ID out of range."
  exit 1
fi

# Calculate indices based on SLURM_ARRAY_TASK_ID
allocation_method_index=$(( SLURM_ARRAY_TASK_ID / (${#spectrum_allocation_priorities[@]} * ${#cores_per_link[@]}) ))
temp_index=$(( SLURM_ARRAY_TASK_ID % (${#spectrum_allocation_priorities[@]} * ${#cores_per_link[@]}) ))
spectrum_priority_index=$(( temp_index / ${#cores_per_link[@]} ))
cores_per_link_index=$(( temp_index % ${#cores_per_link[@]} ))

# Select parameters for this task
allocation_method=${allocation_methods[$allocation_method_index]}
spectrum_priority=${spectrum_allocation_priorities[$spectrum_priority_index]}
cores=${cores_per_link[$cores_per_link_index]}

# Print parameters for this task
echo "Running simulation with:"
echo "  Allocation method: $allocation_method"
echo "  Spectrum priority: $spectrum_priority"
echo "  Cores per link: $cores"

# Move to the project directory
cd ~/Git/SDON_simulator/ || { echo "Failed to change to SDON_simulator directory"; exit 1; }

# Run the simulation with the specified parameters
python run_sim.py --allocation_method "$allocation_method" --spectrum_allocation_priority "$spectrum_priority" --cores_per_link "$cores"

echo "Job completed successfully for SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"

# Deactivate and remove the Conda environment after the job
conda deactivate
conda env remove -n "$env_name"

# Clean up the temporary Conda package directory
rm -rf "/tmp/conda_pkgs_$SLURM_ARRAY_TASK_ID"