<div align="center">
<h1>Wandb Offline Sync Hook</h1>
<em>A convenient way to trigger synchronizations to wandb if your compute nodes don't have internet!</em>
<p></p>

[![Documentation Status](https://readthedocs.org/projects/wandb-offline-sync-hook/badge/?version=latest)](https://wandb-offline-sync-hook.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/wandb-osh.svg)](https://pypi.org/project/wandb-osh)
[![Python 3.8‒3.11](https://img.shields.io/badge/python-3.8%E2%80%923.11-blue)](https://www.python.org)
[![PR welcome](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg)](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/klieret/wandb-offline-sync-hook/main.svg)](https://results.pre-commit.ci/latest/github/klieret/wandb-offline-sync-hook/main)
[![.github/workflows/test.yaml](https://github.com/klieret/wandb-offline-sync-hook/actions/workflows/test.yaml/badge.svg)](https://github.com/klieret/wandb-offline-sync-hook/actions/workflows/test.yaml)
[![link checker](https://github.com/klieret/wandb-offline-sync-hook/actions/workflows/check-links.yaml/badge.svg)](https://github.com/klieret/wandb-offline-sync-hook/actions)
[![codecov](https://codecov.io/github/klieret/wandb-offline-sync-hook/branch/main/graph/badge.svg?token=6MQZ4LODE5)](https://app.codecov.io/github/klieret/wandb-offline-sync-hook)
[![gitmoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg)](https://gitmoji.dev)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

</div>

## 🤔 What is this?

- ✅ You use [`wandb`/Weights & Biases](https://wandb.ai/) to record your machine learning trials?
- ✅ Your ML experiments run on compute nodes without internet access (for example, using a batch system)?
- ✅ Your compute nodes and your head/login node (with internet) have access to a shared file system?

Then this package might be useful. For alternatives, see [below](https://github.com/klieret/wandb-offline-sync-hook#what-alternatives-are-there).

<div align="center">

![](https://user-images.githubusercontent.com/13602468/200086359-507b8653-e999-4cb3-ac93-ba1d175d2016.png)

</div>

### What you might have been doing so far

You probably have been using `export WANDB_MODE="offline"` on the compute nodes and then ran something like

```bash
cd /.../result_dir/
for d in $(ls -t -d */); do cd $d; wandb sync --sync-all; cd ..; done
```

from your head node (with internet access) every now and then.
However, obviously this is not very satisfying as it doesn't update live.
Sure, you could throw this in a `while True` loop, but if you have a lot of trials in your directory, this will take forever, [cause unnecessary network traffic](https://github.com/wandb/wandb/issues/2887) and it's just not very elegant.

### How does `wandb-osh` solve the problem?

1. You add a hook that is called every time an epoch concludes (that is, when we want to trigger a sync).
2. You start the `wandb-osh` script in your head node with internet access. This script will now trigger `wandb sync` upon request from one of the compute nodes.

### How is this implemented?

Very simple: Every time an epoch concludes, the hook gets called and creates a file in a _communication directory_ (`~/.wandb_osh_communication` by default). `wandb-osh` scans the communication directory and reads synchronization instructions from such files.

### What alternatives are there?

With [ray tune][ray-tune], you can use your ray head node as the place to synchronize from (rather than deploying it via the batch system as well, as the [current docs][ray-tune-slurm-docs] suggest). See the note below or my [demo repository][ray-tune-slurm-test].
Similar strategies might be possible for `wandb` as well (let me know!).

## 📦 Installation

```
pip3 install wandb-osh
```

If you want to use this package with `ray`, use

```
pip3 install 'wandb-osh[ray]'
```

## 🔥 Running it!

Two steps: Set up the hook, then run the script from your head node.

### Step 1: Setting up the hook

#### With wandb

Let's adapt the [simple pytorch example](https://docs.wandb.ai/guides/integrations/pytorch) from the wandb docs (it only takes 3 lines!):

```python
import wandb
from wandb_osh.hooks import TriggerWandbSyncHook  # <-- New!


trigger_sync = TriggerWandbSyncHook()  # <--- New!

wandb.init(config=args, mode="offline")

model = ... # set up your model

# Magic
wandb.watch(model, log_freq=100)

model.train()
for batch_idx, (data, target) in enumerate(train_loader):
    output = model(data)
    loss = F.nll_loss(output, target)
    loss.backward()
    optimizer.step()
    if batch_idx % args.log_interval == 0:
        wandb.log({"loss": loss})
        trigger_sync()  # <-- New!
```

#### With pytorch lightning

```python
from wandb_osh.lightning_hooks import TriggerWandbSyncLightningCallback  # <-- New!
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning import Trainer

logger = WandbLogger(
    project="project",
    group="group",
    offline=True,
)

model = MyLightningModule()
trainer = Trainer(
    logger=logger,
    callbacks=[TriggerWandbSyncLightningCallback()]  # <-- New!
)
trainer.fit(model, train_dataloader, val_dataloader)
```

#### With ray tune

> **Note**
> With ray tune, you might not need this package! While the approach suggested in the
> [ray tune SLURM docs][ray-tune-slurm-docs] deploys the ray head on a worker node as well (so it doesn't
> have internet), this actually isn't needed. Instead, you can run the ray head and the
> tuning script on the head node and only submit batch jobs for your workers.
> In this way, `wandb` will be called from the head node and internet access is no
> problem there.
> For more information on this approach, take a look at my [demo repository][ray-tune-slurm-test].

You probably already use the `WandbLoggerCallback` callback. We simply add a second callback for `wandb-osh` (it only takes two new lines!):

```python
import os
from wandb_osh.ray_hooks import TriggerWandbSyncRayHook  # <-- New!


os.environ["WANDB_MODE"] = "offline"

callbacks = [
    WandbLoggerCallback(...),  # <-- ray tune documentation tells you about this
    TriggerWandbSyncRayHook(),  # <-- New!
]

tuner = tune.Tuner(
    trainable,
    tune_config=...,
    run_config=RunConfig(
        ...,
        callbacks=callbacks,
    ),
)
```

#### With anything else

Simply take the `TriggerWandbSyncHook` class and use it as a callback in your training
loop (as in the `wandb` example above), passing the directory that `wandb` is syncing
to as an argument.

### Step 2: Running the script on the head node

After installation, you should have a `wandb-osh` script in your `$PATH`. Simply call it like this:

```
wandb-osh
```

The output will look something like this:

```
INFO: Starting to watch /home/kl5675/.wandb_osh_command_dir
INFO: Syncing /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_b1f60706_4_attr_pt_thld=0.0273,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-08-42
Find logs at: /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_b1f60706_4_attr_pt_thld=0.0273,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-08-42/wandb/debug-cli.kl5675.log
Syncing: https://wandb.ai/gnn_tracking/gnn_tracking/runs/b1f60706 ... done.
INFO: Finished syncing /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_b1f60706_4_attr_pt_thld=0.0273,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-08-42
INFO: Syncing /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_92a3ef1b_1_attr_pt_thld=0.0225,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-07-49
Find logs at: /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_92a3ef1b_1_attr_pt_thld=0.0225,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-07-49/wandb/debug-cli.kl5675.log
Syncing: https://wandb.ai/gnn_tracking/gnn_tracking/runs/92a3ef1b ... done.
INFO: Finished syncing /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_92a3ef1b_1_attr_pt_thld=0.0225,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-07-49
INFO: Syncing /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_a2caa9c0_2_attr_pt_thld=0.0092,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-08-17
Find logs at: /home/kl5675/ray_results/tcn-perfect-test-sync/DynamicTCNTrainable_a2caa9c0_2_attr_pt_thld=0.0092,batch_size=1,focal_alpha=0.2500,focal_gamma=2.0000,gnn_tracking_experiments_has_2022-11-03_17-08-17/wandb/debug-cli.kl5675.log
Syncing: https://wandb.ai/gnn_tracking/gnn_tracking/runs/a2caa9c0 ... done.
```

Take a look at `wandb-osh --help` or check [the documentation](https://wandb-offline-sync-hook.readthedocs.io/en/latest/cli.html) for all command line options.
You can add options to the `wandb sync` call by placing them after `--`. For example

```bash
wandb-osh -- --sync-all
```

## ❓ Q & A

> I get the warning "wandb: NOTE: use wandb sync --sync-all to sync 1 unsynced runs from local directory."

You can start `wandb-osh` with `wandb-osh -- --sync-all` to always synchronize
all available runs.

## 🧰 Development setup

```bash
pip3 install pre-commit
pre-commit install
```

## 💖 Contributing

Your help is greatly appreciated! Suggestions, bug reports and feature requests are best opened as [github issues][github-issues]. You are also very welcome to submit a [pull request][pulls]!

Bug reports and pull requests are credited with the help of the [allcontributors bot](https://allcontributors.org/).

<!-- ## ✨ Contributors -->
<!--  -->
<!-- Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)): -->
<!--  -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/barthelemymp"><img src="https://avatars.githubusercontent.com/u/36533835?v=4?s=100" width="100px;" alt="Barthelemy Meynard-Piganeau"/><br /><sub><b>Barthelemy Meynard-Piganeau</b></sub></a><br /><a href="https://github.com/klieret/wandb-offline-sync-hook/issues?q=author%3Abarthelemymp" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!--  -->
<!-- This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome! -->

[github-issues]: https://github.com/klieret/wandb-offline-sync-hook/issues
[pulls]: https://github.com/klieret/wandb-offline-sync-hook/pulls
[ray-tune-slurm-docs]: https://docs.ray.io/en/latest/cluster/vms/user-guides/community/slurm.html
[ray-tune-slurm-test]: https://github.com/klieret/ray-tune-slurm-test/
[ray-tune]: https://docs.ray.io/en/latest/tune/index.html
