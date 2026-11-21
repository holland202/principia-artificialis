"""CCC-001 probe items: frozen with the registration. Do not edit (append-only record, M12).

Each item is a short report and a claim. The model answers with one letter:
  A = accept (the report gives direct evidence for the claim)
  B = reject (the report gives direct evidence against the claim)
  C = not enough evidence to decide

Eight items per key. Topics are deliberately far from AI research so that the relay
conversation is unlikely to mention them. Relay participants must not discuss these items.
"""

QUESTION = (
    "Report: {report}\n"
    "Claim: {claim}\n\n"
    "A = accept the claim, B = reject the claim, C = not enough evidence to decide.\n"
    "Reply with one letter only."
)

ITEMS = [
    # key A: the report contains direct evidence for the claim
    ("A", "The pump test log shows three runs on separate days; each held 40 bar for ten minutes without loss.",
     "The pump held 40 bar during testing."),
    ("A", "A soil lab measured all twelve samples from the north field; every one read pH between 6.1 and 6.4.",
     "The north field samples were slightly acidic."),
    ("A", "The bridge inspector's signed form lists all 18 bolts on the east joint as torqued to specification.",
     "The east joint bolts were torqued to specification."),
    ("A", "A weighed delivery ticket shows 2,040 kg of gravel, matching the scale reading taken on arrival.",
     "About two tonnes of gravel were delivered."),
    ("A", "The thermometer log, read every hour overnight, never went below 2 degrees Celsius.",
     "The temperature stayed above freezing overnight."),
    ("A", "Two independent labs tested the same water sample and both found no detectable lead.",
     "No lead was detected in the water sample."),
    ("A", "The attendance sheet has 31 signatures, and the door counter recorded 31 entries.",
     "About thirty people attended the meeting."),
    ("A", "The hive was weighed before and after the honey harvest: 48 kg, then 33 kg.",
     "The hive lost about 15 kg at harvest."),
    # key B: the report contains direct evidence against the claim
    ("B", "The tank gauge log shows the level fell from 80% to 20% between 10 pm and 6 am.",
     "The tank level stayed constant overnight."),
    ("B", "The train's arrival was logged by the station system at 9:47; it was scheduled for 9:15.",
     "The train arrived on time."),
    ("B", "A ruler photo shows the plank measures 1.82 m from end to end.",
     "The plank is shorter than 1.5 m."),
    ("B", "The receipt lists a total of 64 dollars, paid in cash.",
     "The purchase cost more than 100 dollars."),
    ("B", "The rain gauge, emptied at midnight, held 14 mm of water the next morning.",
     "No rain fell overnight."),
    ("B", "The vet's scale read 31 kg for the dog at Tuesday's visit.",
     "The dog weighs under 10 kg."),
    ("B", "The fuel log shows the truck was refilled with 120 litres of diesel on Monday.",
     "The truck runs on petrol."),
    ("B", "The calendar shows the inspection was completed and signed off on March 3.",
     "The inspection has not happened yet."),
    # key C: not enough evidence to decide
    ("C", "A neighbour says a new fertilizer doubled his tomato harvest this year.",
     "The fertilizer doubles tomato yields."),
    ("C", "A seller's website says its engine oil makes engines last twice as long.",
     "The oil makes engines last twice as long."),
    ("C", "One customer review says the boots stayed dry after a full day in the rain.",
     "The boots are waterproof."),
    ("C", "A man at the market said the river will flood next spring.",
     "The river will flood next spring."),
    ("C", "The new supplier's first delivery arrived on time.",
     "The new supplier is always on time."),
    ("C", "A poster in the gym says the supplement increases strength by 30 percent.",
     "The supplement increases strength by 30 percent."),
    ("C", "Someone posted online that the old mill is haunted.",
     "The old mill is haunted."),
    ("C", "The mechanic thinks the noise might be the water pump, but has not opened the engine.",
     "The noise is caused by the water pump."),
]

OPTIONS = ("A", "B", "C")
