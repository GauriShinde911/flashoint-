// Multilingual i18n support dictionary (English, Hindi, Marathi)

const I18N_DICTIONARY = {
  en: {
    app_title: "Development Priority Intelligence",
    app_tagline: "Multilingual AI & Deterministic Analytics Platform for DPI",
    select_country: "Country: India",
    filter_state: "State",
    filter_district: "District",
    filter_sector: "Sector",
    filter_quality: "Data Quality",
    all_states: "All States",
    all_districts: "All Districts",
    all_qualities: "All (Real + Synthetic)",
    real_only: "Real Data Only",
    synthetic_only: "Synthetic Only",
    tab_ranked: "Ranked Recommendations",
    tab_silent: "Silent Need Flags",
    tab_mismatch: "Investment-Demand Mismatch",
    tab_impact: "Impact Measurement",
    tab_command: "Policymaker AI Command Center",
    tab_submit: "Submit Citizen Request",
    evidence_title: "District Evidence Panel",
    priority_score: "Priority Score",
    score_breakdown: "Score Component Breakdown",
    why_this_ranking: "Why This Ranking",
    grounded_footnote: "Grounded strictly in verified Census 2011/NFHS-5, National Hospital Directory, and citizen reporting metrics.",
    project_check: "Existing Government Project Check",
    offline_notice: "Offline Demo Mode — Connected to local static mock data."
  },
  hi: {
    app_title: "विकास प्राथमिकता इंटेलिजेंस",
    app_tagline: "डिजिटल पब्लिक इंफ्रास्ट्रक्चर के लिए बहुभाषी एआई और विश्लेषिकी",
    select_country: "देश: भारत",
    filter_state: "राज्य",
    filter_district: "ज़िला",
    filter_sector: "क्षेत्र",
    filter_quality: "डेटा गुणवत्ता",
    all_states: "सभी राज्य",
    all_districts: "सभी ज़िले",
    all_qualities: "सभी (वास्तविक + सिंथेटिक)",
    real_only: "केवल वास्तविक डेटा",
    synthetic_only: "केवल सिंथेटिक",
    tab_ranked: "वरीयता रैंकिंग",
    tab_silent: "मूक आवश्यकताएं",
    tab_mismatch: "निवेश-मांग बेमेल",
    tab_impact: "प्रभाव माप",
    tab_command: "एआई कमांड सेंटर",
    tab_submit: "नागरिक शिकायत भेजें",
    evidence_title: "ज़िला साक्ष्य पैनल",
    priority_score: "प्राथमिकता स्कोर",
    score_breakdown: "घटक विभाजन",
    why_this_ranking: "यह रैंकिंग क्यों है",
    grounded_footnote: "सत्यापित जनगणना 2011/NFHS-5 और अस्पताल निर्देशिका डेटा पर आधारित।",
    project_check: "मौजूदा सरकारी परियोजना जांच",
    offline_notice: "ऑफ़लाइन डेमो मोड — स्थानीय मॉक डेटा से जुड़ा है।"
  },
  mr: {
    app_title: "विकास प्राधान्य बुद्धिमत्ता",
    app_tagline: "डिजिटल पब्लिक इन्फ्रास्ट्रक्चरसाठी बहुभाषिक AI आणि विश्लेषण",
    select_country: "देश: भारत",
    filter_state: "राज्य",
    filter_district: "जिल्हा",
    filter_sector: "क्षेत्र",
    filter_quality: "डेटा गुणवत्ता",
    all_states: "सर्व राज्ये",
    all_districts: "सर्व जिल्हे",
    all_qualities: "सर्व (वास्तविक + सिंथेटिक)",
    real_only: "केवळ वास्तविक डेटा",
    synthetic_only: "केवळ सिंथेटिक",
    tab_ranked: "प्राधान्य क्रमवारी",
    tab_silent: "शांत गरजा",
    tab_mismatch: "गुंतवणूक-मागणी विसंगती",
    tab_impact: "प्रभाव मोजमाप",
    tab_command: "AI कमांड सेंटर",
    tab_submit: "नागरिक तक्रार नोंदवा",
    evidence_title: "जिल्हा पुरावा पॅनेल",
    priority_score: "प्राधान्य गुण",
    score_breakdown: "घटक तपशील",
    why_this_ranking: "ही क्रमवारी का आहे",
    grounded_footnote: "जनगणना 2011/NFHS-5 आणि रुग्णालय निर्देशिका डेटावर आधारित.",
    project_check: "हयात असलेल्या शासकीय योजनांची तपासणी",
    offline_notice: "ऑफलाइन डेमो मोड — स्थानिक मॉक डेटा वापरत आहे."
  }
};

let currentLang = "en";

function setLanguage(lang) {
  if (I18N_DICTIONARY[lang]) {
    currentLang = lang;
    updateUIElements();
  }
}

function t(key) {
  return (I18N_DICTIONARY[currentLang] && I18N_DICTIONARY[currentLang][key]) || I18N_DICTIONARY["en"][key] || key;
}

function updateUIElements() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (key) {
      el.textContent = t(key);
    }
  });
}
