export const SERVICES = [
  {
    id: "residential-care",
    title: "Residential Aged Care",
    description:
      "A permanent home with round-the-clock nursing support, meals, housekeeping and social activities, for people who need daily assistance.",
  },
  {
    id: "respite-care",
    title: "Respite Care",
    description:
      "Short stays that give family carers a break, from a few days to a few weeks, with the same standard of care as our permanent residents.",
  },
  {
    id: "dementia-care",
    title: "Dementia & Cognitive Support",
    description:
      "A calm, secure environment with staff trained in cognitive and behavioural care, tailored to each resident's stage and needs.",
  },
  {
    id: "nursing-care",
    title: "Nursing & Medication Care",
    description:
      "Registered nurses on site to manage medication, wound care and chronic conditions, working closely with each resident's GP.",
  },
  {
    id: "allied-health",
    title: "Allied Health & Wellbeing",
    description:
      "Physiotherapy, podiatry and gentle group activities that help residents stay mobile, active and connected with others.",
  },
  {
    id: "family-support",
    title: "Family Support & Communication",
    description:
      "Regular updates, open visiting hours and a care coordinator who is easy to reach when you have questions.",
  },
];

export const HOW_IT_WORKS_STEPS = [
  {
    title: "Get in touch",
    description:
      "Call us or fill in the form below. A real person will call you back within one business day, not an automated system.",
  },
  {
    title: "We meet and listen",
    description:
      "We visit you or invite you for a tour, talk through your situation, and answer every question, no matter how small.",
  },
  {
    title: "Build a care plan together",
    description:
      "We put together a plan with you and your family, covering the type of care, daily routine and any medical needs.",
  },
  {
    title: "Ongoing care and check-ins",
    description:
      "Care doesn't stop at move-in. We review the plan regularly and keep family updated as needs change over time.",
  },
];

export const WHY_CHOOSE_US_POINTS = [
  "Family-owned and operated since 1998, not a large impersonal chain.",
  "Staff-to-resident ratios that allow real time for each person, not just a checklist.",
  "Every staff member is police-checked, qualified and trained in aged and dementia care.",
  "Open visiting hours, so family can drop in without booking ahead.",
  "One care coordinator per resident, so you always know who to call.",
];

export const TRUST_INDICATORS = [
  "Fully accredited aged care provider",
  "Police-checked, qualified care staff",
  "Registered nurses on site every day",
  "Locally owned and operated since 1998",
];

export const TESTIMONIALS = [
  {
    quote:
      "The team took the time to explain everything to us in plain language, and they still call my mother by her nickname. It stopped feeling like a facility and started feeling like her home.",
    name: "Diane R.",
    relationship: "Daughter of a resident",
  },
  {
    quote:
      "We needed respite care at short notice while I recovered from surgery. They had my father settled in within two days and rang me every evening with an update.",
    name: "Michael T.",
    relationship: "Son of a respite-care client",
  },
  {
    quote:
      "My husband has dementia, and I was terrified of moving him anywhere. The staff here were patient with him from the very first visit, and that made the decision so much easier.",
    name: "Patricia W.",
    relationship: "Wife of a resident",
  },
];

export const FAQS = [
  {
    question: "How do I arrange a tour of the facility?",
    answer:
      "Fill in the appointment form below and choose \"Facility Tour\" as the service, or call us directly. We'll arrange a time that suits you, including evenings and weekends.",
  },
  {
    question: "What types of care do you provide?",
    answer:
      "We offer residential aged care, short-term respite stays, dementia and cognitive support, on-site nursing, and allied health services such as physiotherapy. See the Services section above for details.",
  },
  {
    question: "Is there a waiting list?",
    answer:
      "Availability changes regularly. The best way to get an accurate answer for your situation is to contact us directly, we're always upfront about current wait times.",
  },
  {
    question: "Can family visit at any time?",
    answer:
      "Yes. We keep visiting hours open and flexible, because we know how important it is for family to be able to drop in without booking ahead.",
  },
  {
    question: "How is the cost of care worked out?",
    answer:
      "Costs depend on the type of care and any government funding you're eligible for, such as a Home Care Package or residential aged care subsidy. Our team can walk you through your options in plain language, with no obligation.",
  },
  {
    question: "What if my loved one has dementia or memory loss?",
    answer:
      "Our staff are trained specifically in dementia and cognitive care, and our dementia support areas are designed to feel calm and familiar rather than clinical.",
  },
];

export const APPOINTMENT_SERVICE_OPTIONS = [
  ...SERVICES.map((service) => service.title),
  "Facility Tour",
  "General Enquiry",
];

export const IMPACT_STATS = [
  { value: "27 years", label: "Caring for South Australian families since 1998" },
  { value: "1,400+", label: "Residents and in-home clients supported" },
  { value: "320", label: "Qualified care staff, all police-checked" },
  { value: "9", label: "Homes and community sites across the state" },
];
