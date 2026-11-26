# TOR-001 outside material: the post that prompted the question (C-EXT)

**What was received.** On 2026-11-26, Chad Holland gave Claude a phone screenshot of a public LinkedIn post. The
SHA-256 of the image file as received is `89d337a421132b9d835e54638a510ffd8e7898c4ca1ca30e594566611a821170`. The
image is **not committed**, because it shows other people's profile photos (C-PRIVATE). The post's URL has not been
supplied yet, and the post's full text is cut off ("… more") in the screenshot.

**Visible text, transcribed by Claude from the screenshot (not a verified quote):**

- The reshare, from an account whose name is cut off and whose headline begins "Geometric Deep Learning, World
  Models, …": "While variational autoencoder assume the latent values follow a Gaussian distribution, this model
  enforces a geometry and symmetry of a low dimensional… more"
- The original post, by **Sushil Pershad**: "Why a model might store a field on a torus. The field is two travelling
  waves. Its whole… more"
- **The figure**, titled "Manifold latent space", with the subtitle "Encode a field, project onto the manifold,
  evolve, decode":
  - an input field u(t), encoded onto the latent space "M = T² (torus)", evolved there and decoded to a prediction
    û(t+Δt);
  - a pipeline: Initial Field → Convolutional Layers → MLP → Manifold Latent → MLP → Transpose Conv → Predicted Field,
    grouped as Encoder, Dynamics and Decoder;
  - its equations: z = P_M(E(u)); θ̇ = ω on T²; û(t+Δt) = D(z(t+Δt)); u(x, y, t) = 0.6 sin(x + y − θ₁) +
    0.4 sin(2x − y − θ₂); "Two travelling waves ⇒ two phases (θ₁, θ₂) ⇒ every state lies on a torus";
  - a watermark, "@mathemetica".

**Authorship (LINEAGE):** the question is credited to Sushil Pershad's post. The figure's original author is
INDETERMINATE, because of the watermark. Crediting the question implies no endorsement or validation of this work by
either person.

**Claims in the post, checked row by row:** none were checked by running anything (NOT RUN). One is VERIFIED FROM
SOURCE as mathematics: the field shown is 0.6·(sin(x+y)cos θ₁ − cos(x+y)sin θ₁) + 0.4·(…). That is a linear
combination of four fixed spatial patterns, with coefficients (cos θᵢ, sin θᵢ). So its states lie on a torus embedded
*linearly* in a 4-dimensional subspace. This is why the registration adds a linear rival.

## Changes (W9)

- **2026-11-26, the post's URL.** Chad Holland supplied it on PR #186 (comment 7196893238):
  `https://lnkd.in/p/gh3wU6Y5`, Sushil Pershad, "Why a model might store a field on a torus". The link is a LinkedIn
  short link and was not opened from here. The text above is still the transcription from the screenshot. The earlier
  line "The post's URL has not been supplied yet" is superseded.
