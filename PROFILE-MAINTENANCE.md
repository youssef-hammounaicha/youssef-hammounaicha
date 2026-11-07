# Profile maintenance

This repository contains the public profile only. No private project source is required.

## Identity and content

The public repository name must match the account: `youssef-hammounaicha`.
README project descriptions and technologies are taken from the previous public README.
No demo links, shipping claims, availability metrics or private source links have been added.
The original PNG remains unchanged and is displayed inside the credits disclosure.

## Images and accessibility

Custom SVGs are standalone images with internal CSS, system font fallbacks, titles,
descriptions and no JavaScript, foreignObject, embedded external resources or remote fonts.
Mobile artwork is selected by native picture/source media queries. GitHub controls the
surrounding Markdown page: a README cannot force GitHub's whole page into dark mode.
Header and terminal animations stop after their introductory sequence. Reduced motion
disables them. The snake has a separate static alternative. Text descriptions remain
available in Markdown and image alternatives.

## Automation

The contribution workflow runs daily at 04:23 UTC, on manual dispatch, and when its own
configuration changes on main. It uses the repository-scoped GITHUB_TOKEN, with read
permissions by default and contents:write for its single publishing job. No PAT is needed.
Checkout and Platane/snk are pinned to full commit hashes. Only the two snake SVGs are
staged. Generated commits cannot create a push loop because of the workflow path filter.
Relative asset paths survive repository renaming.

The repository must allow GitHub Actions and the two pinned actions. Branch protection
must permit the bot to update main, otherwise adapt publication to a pull-request flow.
Do not weaken protections automatically. Check Actions after changing this workflow.
Scheduled runs may be delayed by GitHub and are disabled after 60 days of inactivity in
public repositories. Re-enable the schedule if GitHub disables it.

If generation fails, the last successful SVG remains available; before the first run,
an explicitly labeled placeholder is displayed. Never substitute invented activity.

## Credits

- Original banner retained from this repository.
- Original SVG implementation; panel concept inspired by saroo98/profile-signal-kit.
- Snake generation: Platane/snk (MIT), pinned dependency; source not vendored.
