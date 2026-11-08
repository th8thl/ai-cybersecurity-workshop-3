# Case discussion: EchoLeak

Microsoft identifies CVE-2025-32711 as a Microsoft 365 Copilot information-disclosure vulnerability. Use the [Microsoft security advisory](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-32711) and the researchers' [Aim Labs disclosure](https://www.aim.security/lp/aim-labs-echoleak-blogpost) as the primary reading. The disclosure site may restrict automated access; open it in the browser before class. The case-study paper [EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System](https://arxiv.org/abs/2509.10540) supplies an additional technical account.

Discuss how attacker-controlled external content can enter an assistant's context, be mistaken for instructions, and cross an information-disclosure boundary. Map those boundaries to the workshop's retrieved document, MCP tool result, model prompt and output path. Explain which controls address access and which only inspect content.

The local lab does not reproduce the Microsoft exploit chain or claim that a phrase filter fixes it. Students demonstrate the underlying trust-boundary problem with synthetic documents and no real exfiltration. Ask what additional threat modeling and evidence would be needed for an enterprise deployment.
