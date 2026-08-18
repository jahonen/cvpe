---
title: "The Model Is a Constitution: Why Europe Cannot Rent Its Values"
slug: model-is-a-constitution
date: 2026-08-18
modified: 2026-08-18
domain: Sovereignty
excerpt: "A frontier model's value profile is a written document, drafted in one jurisdiction, under one legal system, anticipating one regulator. Europe can license the software. It cannot license the judgement encoded inside it."
bluesky_thread: ""
prediction: false
prediction_status: ""
reading_time: 13
guest: false
---

There is a comfortable assumption underneath most European AI procurement: that a large language model is a tool, and that tools are neutral. Buy the best one available, apply European rules to how it is used, and [sovereignty is a matter of where the data sits](/essays/patch-as-hostage-sovereignty-hyperscale/) and who holds the contract.

This is wrong, and the reason it is wrong is not mystical. It is documented, in public, by the companies themselves.

---

## The Values Are Not Emergent. They Are Written Down.

A common version of this argument holds that because models are trained on different data, they absorb different cultural assumptions. That version is weak, and it should be abandoned rather than defended. Frontier labs train on broadly overlapping corpora — the same public web, the same books, the same code. And it is true but nearly meaningless that two training runs produce different weights: random initialisation alone guarantees numerical divergence between two models with functionally identical values. Uniqueness of parameters is not evidence of cultural specificity. Anyone making that argument in front of a technical audience will lose, and deserve to.

The real mechanism sits later in the pipeline, and it is far harder to dismiss, because it is not emergent at all. It is authored.

What a model will and will not say, how it weighs competing claims, where it refuses, what it treats as settled and what it treats as contested — these are set during post-training: the alignment stage, where a lab specifies the behaviour it wants and trains the model toward it. And the frontier labs do not hide this. Anthropic publishes [a constitution for its models](https://www.anthropic.com/news/claudes-constitution). OpenAI publishes [a model specification](https://model-spec.openai.com/). These are written documents. They are drafted by identifiable organisations, incorporated in identifiable jurisdictions, employing annotator populations recruited under particular labour markets, anticipating liability under particular courts, and calibrating refusals against particular regulators.

A model's value profile is therefore not an accident of the data. It is a policy document, executed in weights.

Once that is clear, the European question stops being philosophical and becomes concrete. American constitutional law treats speech restrictions with a suspicion that German and French law do not share; a model calibrated to First Amendment intuitions will draw the line on hateful speech in a place that does not match the Strafgesetzbuch or the Loi Gayssot. American privacy practice treats personal data as a commodity with contractual protections; GDPR treats it as a fundamental right with structural ones. A model's defaults on what it will infer, retain, or volunteer about a person reflect one of those two starting points, not both. On colonial history, on contested territory, on the legitimacy of political violence in specific historical cases, on the balance between free expression and dignity — a model gives answers, and those answers were shaped by someone, somewhere, working under a particular set of legal and commercial incentives.

None of this requires bad faith from any lab. An American company writing an American document under American law, anticipating an American regulator, is doing exactly what a well-run American company should do. The point is narrower and harder to escape: the artefact it produces is not jurisdictionally neutral, and using it at scale in Europe means adopting a set of value judgements Europe did not make, cannot inspect in full, and cannot amend.

Europe can license the software. It cannot license the judgement encoded inside it.

---

## What This Is Not

This is not an argument that American models are hostile, badly built, or unsafe. They are, by most measures, the most capable systems available, and European institutions currently use them for good reasons.

Nor is it an argument that a European model would be neutral. It would not be. It would encode European value judgements — which is precisely the point, and precisely why the question of who writes that specification, under what democratic accountability, is a governance question rather than a procurement one.

And it is not a natural monopoly argument. It is worth being explicit about this, because [this site has made natural-monopoly arguments elsewhere](/a-certain-vision/natural-monopolies/) and the term should not be stretched to cover things it does not fit. A natural monopoly exists where duplication is inherently wasteful and competition structurally impossible — the second set of distribution cables down the same street, the second water main. Frontier models fail that test plainly. There are several frontier labs competing right now, entry has repeatedly occurred, and the competition between them is producing real capability gains. Anyone claiming frontier models are a natural monopoly is describing a market that visibly does not exist.

The layer underneath them is a different matter. Gigawatt-scale compute, grid connections, and the power infrastructure that feeds them have genuine natural-monopoly characteristics, in exactly the way [generation and grid differ](/a-certain-vision/natural-monopolies/): you can build many competing generators, but running competing sets of high-voltage transmission to the same place is waste. Models are generation. The compute substrate is closer to the wires. That distinction matters for what Europe should own outright versus what it should merely fund well.

So the case for a European frontier model is not that only one can exist. It is that Europe can afford to do this properly approximately once, and should therefore decide deliberately rather than by accident.

---

## Strategic Resourcing, Not Market Structure

[Mistral](https://mistral.ai/) is the concrete instance of this question, not a hypothetical.

The company is European-incorporated, ships open-weight models that can run on European infrastructure under European jurisdiction, and has built its commercial identity around exactly the sovereignty proposition this essay describes. Its last confirmed valuation was €11.7 billion, following a €1.7 billion Series C in September 2025 led by [ASML](https://www.asml.com/en) — the Dutch lithography firm taking roughly an 11% stake, which is industrial policy wearing a venture capital suit. A substantially larger round at around €20 billion was reported in talks during mid-2026; at the time of writing it has not been confirmed closed, and it should not be treated as fact. Revenue has grown steeply, with annual recurring revenue reported crossing $400 million in early 2026 against a stated target above $1 billion. The company has taken on €722 million in debt financing, backed by [Bpifrance](https://www.bpifrance.fr/) and BNP Paribas, to build Nvidia-powered data centres in France and Sweden, targeting 200MW of compute capacity by 2027.

Set against American comparators, the asymmetry is stark rather than encouraging. Mistral's capital base is a fraction of OpenAI's or Anthropic's. Its compute ambitions are measured in hundreds of megawatts where American buildouts are measured in gigawatts. This is not a company that will win a spending race, and pretending otherwise helps no one.

Which is exactly why the resourcing question is strategic rather than structural. Europe is not choosing between one champion and a competitive market — it is choosing between one adequately funded champion and several underfunded ones. The EU's [AI Continent Action Plan](https://digital-strategy.ec.europa.eu/en/policies/ai-continent-action-plan) commits roughly €20 billion across member states, with thirteen AI factories funded through [EuroHPC](https://eurohpc-ju.europa.eu/). Germany has Aleph Alpha and Black Forest Labs. The UK has Stability. Each is real; none is close to frontier scale. Distributing European resources evenly across a field of national champions, each chasing the same frontier with a fraction of the necessary capital, is the reliable way to produce several second-tier labs and no first-tier one.

That is a choice about allocation under scarcity. It has nothing to do with whether competition is possible in principle, and everything to do with whether Europe's actual available capital, concentrated, clears the threshold that matters.

---

## The Commenda Problem

If Europe concentrates public capital behind a private frontier lab, it runs directly into a problem this site has described before: public money underwrites the risk, private shareholders capture the return, and the public ends up holding neither ownership nor leverage over an asset it paid to create.

The historical answer to precisely this problem is European, and it is old.

The commenda emerged in the Italian maritime republics in the twelfth century — the earliest documented example in Genoa in 1156 — to solve a structurally identical situation. Long-distance trade offered enormous returns and catastrophic risk. Ships sank. One party held capital but could not or would not sail; the other had the skill and willingness to sail but not the capital. The contract paired a sedentary investor with a travelling merchant, splitting profits on agreed proportions, with the investor's losses limited to the stake contributed. In Genoa, notarial records between 1154 and 1315 document over 8,400 sea-venture partnerships, more than 93% of them structured as commenda. The bilateral variant, where the travelling merchant contributed capital of his own, split profits evenly and shared losses — the terms tracked who actually bore what risk.

Its significance was not just efficiency. It was participation. The commenda let nobles, widows, artisans, and religious houses invest in ventures they could not personally undertake, broadening capital formation well beyond the merchant elite. The structure proved durable enough to survive centuries and to be recognisably reinvented as modern private equity.

What the commenda encoded, and what modern public-private arrangements routinely fail to encode, is that the party bearing the risk holds a permanent, proportionate claim on the return. Not a subsidy. Not a grant that quietly becomes someone's private fortune. A stake.

Applied to a European frontier lab, [the principle](/a-certain-vision/new-commenda/) implies a small number of specific commitments, which this essay states rather than elaborates. Public capital enters as equity, not grant. The public stake is permanent and proportionate to risk borne, not diluted away in subsequent rounds. Losses fall where the capital was committed, as they did in the original contract. And critically for the argument above: the alignment specification — the written value document that determines what the model actually does — is subject to democratic accountability, because that document is where sovereignty either exists or doesn't. [Ownership of the company without visibility into the specification](/lexicon/ownership-control-criterion/) would be ownership of the shell rather than the substance.

The ASML stake in Mistral is instructive precisely because it is halfway there. A European industrial anchor taking 11% of a European frontier lab is the right instinct, executed as ordinary venture investment rather than as a structured public claim with governance attached. The instinct is sound. The structure is not yet the commenda.

---

## What Follows

Europe's AI debate has been conducted almost entirely as a capability race — can Europe catch up, how much compute, how many gigawatts, whose champion. That framing is not wrong, but it is downstream of a prior question that has barely been asked in public: who writes the specification.

A frontier model deployed across European public administration, healthcare, education, and courts will make millions of small judgement calls a day, each reflecting a value document drafted by someone. If that document was written in San Francisco under American law, European institutions will be running on American judgement, at scale, invisibly, in a way no procurement clause reaches and [no data-residency guarantee touches](/lexicon/ownership-control-criterion/).

That is the actual sovereignty question. It is not where the weights are stored. It is whose constitution they encode.

---

*JP Ahonen is a transformation director, Finnish defence reservist, and independent analyst based in Porto Rafti, Greece.*
