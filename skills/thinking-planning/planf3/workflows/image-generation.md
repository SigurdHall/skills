# Image Generation

Fill or update the embedded images in an existing plan `.html` file. Pick the sub-workflow based on the incoming `USER_PROMPT`:

| Sub-workflow | When to call it |
| --- | --- |
| Create | The prompt asks to generate, fill, or add the plan's images from scratch (empty `{{...IMAGE` slots) |
| Update | The prompt asks to change, refine, regenerate, or replace images that already exist in the plan |

Primary path - Codex built-in `image_gen` (runs on the ChatGPT subscription, no API key):
- Create image: `codex exec --skip-git-repo-check "Use your built-in image_gen tool to generate: <prompt>. Save the image to <absolute output path>. Reply only with the saved path."`
- Edit image: `codex exec --skip-git-repo-check -i <input.png> "Use your built-in image_gen tool to edit the attached image: <instruction>. Save the result to <absolute output path>. Reply only with the saved path."`
- Always pass absolute output paths. If Codex cannot write the file (its sandbox may fail to initialize inside a container), the generated PNG still lands in `~/.codex/generated_images/<session>/` - copy the newest PNG from there to the output path yourself. Verify the output file exists and is non-empty before embedding.

Fallback - direct OpenAI API scripts, only when `OPENAI_API_KEY` is set (env or `.env` in the project cwd):
- Create image: `uv run scripts/generate_gpt_image.py "<prompt>" <output.png> --size 1536x1024 --quality high`
- Edit image: `uv run scripts/edit_gpt_image.py "<instruction>" <output.png> <input.png> --size 1536x1024 --quality high`

If neither path is available, skip this workflow: leave the commented `{{...IMAGE}}` placeholders in place and note in the report that images were skipped. Do not fail the plan on missing images.

Shared rules for every image prompt:
- always generate in wide format at high quality: ask for "wide 1536x1024 landscape" in the codex prompt, or pass `--size 1536x1024 --quality high` to the scripts
- convey the one or two core ideas of that section for a professional software engineer
- match the plan's synced visual identity (professional, focused, minimal)
- keep total words shown in the image under 10
- save images to `IMAGES_OUTPUT_DIR` (create it if missing)

## Create

1. Find slots - Grep the plan for `{{...IMAGE` placeholders (hero + per-phase). Each comment names the intended subject.
2. Write prompts - For each slot, write a prompt following the shared rules above.
3. Generate - Run `generate_gpt_image.py` once per slot, writing to `IMAGES_OUTPUT_DIR`.
4. Embed - Replace each `<!-- {{...IMAGE: ...}} -->` placeholder with `<img src="<plan-name>/<file>.png" alt="...">`, keeping the existing `<figure>`/`<figcaption>`.
5. Report - List the images generated and the slots filled.

## Update

1. Identify targets - From the `USER_PROMPT`, determine which embedded `<img>` images to change.
2. Write instruction - Write an edit instruction describing the change, following the shared rules above.
3. Edit - Run `edit_gpt_image.py` with the existing PNG as input, overwriting it (the script backs up the original first).
4. Verify embed - Confirm the `<img>` still points at the updated file; update `src`/`alt`/`<figcaption>` if the change warrants it.
5. Report - List the images updated and what changed.
