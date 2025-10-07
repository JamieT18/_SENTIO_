import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      "title": "Sentio Admin Dashboard",
      "subtitle": "Control pricing, plans, and subscription logic here.",
      "pricingPlans": "Pricing & Plans",
      "planFree": "Free: Basic features",
      "planStandard": "Standard: Advanced analytics",
      "planPro": "Pro: Full trading engine",
      "planElite": "Elite: All features + priority support",
      "subscriptionControls": "Subscription Controls",
      "updatePricing": "Update Pricing",
      "managePlans": "Manage Plans",
      "viewSubscribers": "View Subscribers",
      "language": "Language"
    }
  },
  es: {
    translation: {
      "title": "Panel de Administración de Sentio",
      "subtitle": "Controle los precios, planes y lógica de suscripción aquí.",
      "pricingPlans": "Precios y Planes",
      "planFree": "Gratis: Características básicas",
      "planStandard": "Estándar: Análisis avanzado",
      "planPro": "Pro: Motor de trading completo",
      "planElite": "Elite: Todas las funciones + soporte prioritario",
      "subscriptionControls": "Controles de Suscripción",
      "updatePricing": "Actualizar Precios",
      "managePlans": "Administrar Planes",
      "viewSubscribers": "Ver Suscriptores",
      "language": "Idioma"
    }
  },
  fr: {
    translation: {
      "title": "Tableau de Bord Admin Sentio",
      "subtitle": "Contrôlez les prix, les plans et la logique d'abonnement ici.",
      "pricingPlans": "Prix et Plans",
      "planFree": "Gratuit: Fonctionnalités de base",
      "planStandard": "Standard: Analyses avancées",
      "planPro": "Pro: Moteur de trading complet",
      "planElite": "Elite: Toutes les fonctionnalités + support prioritaire",
      "subscriptionControls": "Contrôles d'Abonnement",
      "updatePricing": "Mettre à Jour les Prix",
      "managePlans": "Gérer les Plans",
      "viewSubscribers": "Voir les Abonnés",
      "language": "Langue"
    }
  },
  de: {
    translation: {
      "title": "Sentio Admin-Dashboard",
      "subtitle": "Steuern Sie hier Preise, Pläne und Abonnementlogik.",
      "pricingPlans": "Preise & Pläne",
      "planFree": "Kostenlos: Grundfunktionen",
      "planStandard": "Standard: Erweiterte Analysen",
      "planPro": "Pro: Vollständige Trading-Engine",
      "planElite": "Elite: Alle Funktionen + Priority Support",
      "subscriptionControls": "Abonnement-Kontrollen",
      "updatePricing": "Preise Aktualisieren",
      "managePlans": "Pläne Verwalten",
      "viewSubscribers": "Abonnenten Anzeigen",
      "language": "Sprache"
    }
  },
  zh: {
    translation: {
      "title": "Sentio 管理仪表板",
      "subtitle": "在此控制定价、计划和订阅逻辑。",
      "pricingPlans": "定价和计划",
      "planFree": "免费：基本功能",
      "planStandard": "标准：高级分析",
      "planPro": "专业：完整交易引擎",
      "planElite": "精英：所有功能 + 优先支持",
      "subscriptionControls": "订阅控制",
      "updatePricing": "更新定价",
      "managePlans": "管理计划",
      "viewSubscribers": "查看订阅者",
      "language": "语言"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
