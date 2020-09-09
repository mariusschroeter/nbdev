# Release notes

<!-- do not remove -->

## 1.0.13

### New Features

- remove numpy conda dep and update to fastcore 1.0.5 ([#241](https://api.github.com/repos/fastai/nbdev/issues/241))

### Bugs Squashed

- allow nbdev imports when not in an nbdev project ([#238](https://api.github.com/repos/fastai/nbdev/issues/238))

## 1.0.10

### New Features

- Magic flags for tests ([#232](https://github.com/fastai/nbdev/pull/232))
  - See [the docs](https://nbdev.fast.ai/magic_flags.html) for details

- Add ability to have Colab badges on pages ([#210](https://github.com/fastai/nbdev/pull/210))
  - See [the docs](https://nbdev.fast.ai/#Google-Colab-Badges) for details

- Support for `doc_path` ([#235](https://github.com/fastai/nbdev/pull/235))
  - Place doc template in path pointed to by `doc_path` if you need your template in a different location to your built docs

### Bugs Squashed

- Remove colab vendor specific tags which cause `nbdev_build_docs` to fail ([#207](https://github.com/fastai/nbdev/pull/207))

- hooks folder inside .git must be manually created before `nbdev_install_git_hooks` ([#230](https://github.com/fastai/nbdev/pull/230))

- updates to how backtick names are converted to doc links ([#218](https://github.com/fastai/nbdev/pull/218))

## Version 1.0.0

- Initial release

