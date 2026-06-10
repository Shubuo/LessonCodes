# Multipass VM Runbook (Mininet - UAV - MDS)

This runbook outlines the required commands to execute the Mininet simulation within the `mininet-vm` environment and safely copy the results back to the local machine.

## Prerequisites
- Multipass is installed on your Mac.
- The `mininet-vm` instance is running (`multipass info mininet-vm`).

## Step 1: Connect and Run the Experiment
You can execute the automated simulation using `multipass exec`. This is useful for **extracting data and generating logs/graphs**, but not ideal for a live presentation demo.

```bash
multipass exec mininet-vm -- bash -c "cd /home/ubuntu/mininet-uav-exp && sudo python3 run_mininet_uav_experiment.py"
```

*Note: You may need to provide your `sudo` password if prompted inside the VM, or run it through `multipass shell` manually.*

```bash
multipass shell mininet-vm
cd /home/ubuntu/mininet-uav-exp
sudo python3 run_mininet_uav_experiment.py
```

## Step 2: Backup Existing Results (Timestamping)
To prevent overwriting older results, always backup the existing `results` folder inside the VM before a new run, or move the newly generated results to a timestamped folder:

```bash
multipass exec mininet-vm -- bash -c "cd /home/ubuntu/mininet-uav-exp && mv results results_$(date +%Y%m%d_%H%M%S)"
```

## Step 3: Copy Results to Local Machine
Once the simulation is completed, you need to extract `measurements.csv`, `summary.json`, and any raw logs. Use the `multipass transfer` command to copy them to your Mac.

```bash
# Ensure local assets folder exists
mkdir -p /Users/buraky/AdvNetworks/mininet-sunum/assets/mininet-results

# Copy from VM to Local
multipass transfer -r mininet-vm:/home/ubuntu/mininet-uav-exp/results /Users/buraky/AdvNetworks/mininet-sunum/assets/mininet-results
```

## 🎥 Step 4: Live Demo Execution (For Presentations)
Running the automated Python script during a presentation may be visually boring for the audience (it just prints text logs). To show the **Live SDN Slicing effect**, you should use the interactive iperf method.

A dedicated and highly detailed step-by-step guide on how to perform this live demo (what to type, where to point on the screen, and what to say) has been created in:
👉 **[Mininet_Canli_Demo_Rehberi.md](./Mininet_Canli_Demo_Rehberi.md)**

Please refer to that document to practice your live demonstration.

## Troubleshooting
- **Missing dependencies for MDS**: If MDS simulation is required on the VM, ensure you have the python packages installed:
  ```bash
  multipass exec mininet-vm -- bash -c "pip3 install simpy pandas tqdm"
  ```
- **Permission errors on Mininet**: Always run Mininet scripts (`mn`) with `sudo`. Also, if you run `sudo mn -c` it clears stale Mininet states which can fix hanging issues.
