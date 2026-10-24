# Owner-provided VMRX branding assets

The images below were supplied by the project operator for VMRX branding. Verify appropriate rights before reuse by third parties. The app icon and README use `assets/vmrx-logo.png`.

- `vmrx-branding-01.png`
- `vmrx-branding-02.png`
- `vmrx-branding-03.png`
- `vmrx-logo.png`

## Transparent official PNGs

All five original 1254 × 1254 owner-supplied PNG assets were preserved at their
original dimensions and converted to **real RGBA transparency** by selectively
removing dark, border-connected backgrounds. The owner artwork's colored regions
were preserved; no externally generated substitute logo was used.

Main README and GUI logo: `assets/vmrx-logo.png`.
Additional formats/variants: `assets/branding/*.png`.
Windows ICO generation uses this same transparent PNG and will retain its alpha.
Black backgrounds should no longer appear around the icon on white GitHub pages.
The original image paths remain unchanged for backward-compatible references.

Automated verification: `scripts/transparent_png_logos.py` +
`.github/workflows/transparent-logos.yml`; GitHub Actions checks alpha=0
at the image corners and nonempty artwork before committing.
