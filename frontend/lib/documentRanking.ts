/**
 * Document ranking and organization utilities
 * Classifies documents by strategic levels: Strategic -> Product -> Developer -> User -> Operations
 */

import { DocumentTemplate } from './api';

export type ViewMode = 'all' | 'team' | 'solo';

// Document Level Classification
export enum DocumentLevel {
  STRATEGIC = 1,      // Level 1: Strategic (Entrepreneur/CEO)
  PRODUCT = 2,        // Level 2: Product Manager
  DEVELOPER = 3,      // Level 3: Developer/Technical
  USER = 4,          // Level 4: User/End-user
  OPERATIONS = 5,    // Level 5: Operations/Maintenance
  CROSS_LEVEL = 0,   // Cross-level (Everyone)
}

// Map document IDs to their strategic levels
const DOCUMENT_LEVEL_MAP: Record<string, DocumentLevel> = {
  // Level 1: Strategic (Entrepreneur/CEO)
  'requirements': DocumentLevel.STRATEGIC,
  'project_charter': DocumentLevel.STRATEGIC,
  'business_model': DocumentLevel.STRATEGIC,
  'marketing_plan': DocumentLevel.STRATEGIC,
  'gtm_strategy': DocumentLevel.STRATEGIC,
  'stakeholders_doc': DocumentLevel.STRATEGIC,
  'stakeholder_communication': DocumentLevel.STRATEGIC,
  'risk_management_plan': DocumentLevel.STRATEGIC,
  'change_management_plan': DocumentLevel.STRATEGIC,
  'feature_roadmap': DocumentLevel.STRATEGIC,
  'pm_management_doc': DocumentLevel.STRATEGIC,
  'wbs': DocumentLevel.STRATEGIC,
  
  // Level 2: Product Manager
  'user_stories': DocumentLevel.PRODUCT,
  'prd': DocumentLevel.PRODUCT,
  'fsd': DocumentLevel.PRODUCT,
  'pm_documentation': DocumentLevel.PRODUCT,
  'user_analytics': DocumentLevel.PRODUCT,
  'dashboard_metrics': DocumentLevel.PRODUCT,
  'kpi_metrics_doc': DocumentLevel.PRODUCT,
  'release_notes': DocumentLevel.PRODUCT,
  'user_feedback_plan': DocumentLevel.PRODUCT,
  'ab_testing_docs': DocumentLevel.PRODUCT,
  'onboarding_flow': DocumentLevel.PRODUCT,
  'interaction_flows': DocumentLevel.PRODUCT,
  'ui_mockups': DocumentLevel.PRODUCT,
  'ui_style_guide': DocumentLevel.PRODUCT,
  
  // Level 3: Developer/Technical
  'technical_documentation': DocumentLevel.DEVELOPER,
  'tad': DocumentLevel.DEVELOPER,
  'api_documentation': DocumentLevel.DEVELOPER,
  'database_schema': DocumentLevel.DEVELOPER,
  'developer_guide': DocumentLevel.DEVELOPER,
  'developer_documentation': DocumentLevel.DEVELOPER,
  'setup_guide': DocumentLevel.DEVELOPER,
  'test_plan': DocumentLevel.DEVELOPER,
  'test_documentation': DocumentLevel.DEVELOPER,
  'cicd_doc': DocumentLevel.DEVELOPER,
  'api_versioning_policy': DocumentLevel.DEVELOPER,
  'configuration_management_plan': DocumentLevel.DEVELOPER,
  'deployment_plan': DocumentLevel.DEVELOPER,
  'scalability_plan': DocumentLevel.DEVELOPER,
  'technical_debt_log': DocumentLevel.DEVELOPER,
  'third_party_integrations': DocumentLevel.DEVELOPER,
  'feature_flag_docs': DocumentLevel.DEVELOPER,
  
  // Level 4: User/End-user
  'user_documentation': DocumentLevel.USER,
  'user_support_doc': DocumentLevel.USER,
  'knowledge_base': DocumentLevel.USER,
  'support_training_doc': DocumentLevel.USER,
  
  // Level 5: Operations/Maintenance
  'backup_recovery_plan': DocumentLevel.OPERATIONS,
  'maintenance_plan': DocumentLevel.OPERATIONS,
  'monitoring_logging_plan': DocumentLevel.OPERATIONS,
  'performance_optimization_doc': DocumentLevel.OPERATIONS,
  'cloud_infrastructure_doc': DocumentLevel.OPERATIONS,
  'bcp': DocumentLevel.OPERATIONS,
  'sla': DocumentLevel.OPERATIONS,
  'vendor_management_docs': DocumentLevel.OPERATIONS,
  'incident_response_plan': DocumentLevel.OPERATIONS,
  'data_retention_policy': DocumentLevel.OPERATIONS,
  'data_governance_policy': DocumentLevel.OPERATIONS,
  
  // Security/Compliance (can be multiple levels, default to Operations)
  'security_plan': DocumentLevel.OPERATIONS,
  'privacy_policy': DocumentLevel.OPERATIONS,
  'terms_of_service': DocumentLevel.OPERATIONS,
  'legal_compliance': DocumentLevel.OPERATIONS,
  'accessibility_plan': DocumentLevel.OPERATIONS,
  'eol_policy': DocumentLevel.OPERATIONS,
  'localization_plan': DocumentLevel.OPERATIONS,
  'technical_audit': DocumentLevel.OPERATIONS,
  
  // Cross-level (Everyone)
  'support_playbook': DocumentLevel.CROSS_LEVEL,
  'quality_review': DocumentLevel.CROSS_LEVEL,
  'document_improver': DocumentLevel.CROSS_LEVEL,
  'format_converter': DocumentLevel.CROSS_LEVEL,
  'code_analyst': DocumentLevel.CROSS_LEVEL,
};

// Level names for display
export const LEVEL_NAMES: Record<DocumentLevel, string> = {
  [DocumentLevel.STRATEGIC]: 'Level 1: Strategic (Entrepreneur/CEO)',
  [DocumentLevel.PRODUCT]: 'Level 2: Product Manager',
  [DocumentLevel.DEVELOPER]: 'Level 3: Developer/Technical',
  [DocumentLevel.USER]: 'Level 4: User/End-user',
  [DocumentLevel.OPERATIONS]: 'Level 5: Operations/Maintenance',
  [DocumentLevel.CROSS_LEVEL]: 'Cross-Level (Everyone)',
};

// Level icons
export const LEVEL_ICONS: Record<DocumentLevel, string> = {
  [DocumentLevel.STRATEGIC]: '🎯',
  [DocumentLevel.PRODUCT]: '📊',
  [DocumentLevel.DEVELOPER]: '💻',
  [DocumentLevel.USER]: '👤',
  [DocumentLevel.OPERATIONS]: '⚙️',
  [DocumentLevel.CROSS_LEVEL]: '🌐',
};

/**
 * Get document level from document ID or category
 */
export function getDocumentLevel(doc: DocumentTemplate | string): DocumentLevel {
  // Handle string input (document ID)
  if (typeof doc === 'string') {
    if (doc in DOCUMENT_LEVEL_MAP) {
      return DOCUMENT_LEVEL_MAP[doc];
    }
    // Default to cross-level if not found
    return DocumentLevel.CROSS_LEVEL;
  }
  
  // Try direct ID match first
  if (doc.id in DOCUMENT_LEVEL_MAP) {
    return DOCUMENT_LEVEL_MAP[doc.id];
  }
  
  // Try category-based classification
  const category = (doc.category || '').toLowerCase();
  if (category.includes('项目管理') || category.includes('project management')) {
    return DocumentLevel.STRATEGIC;
  }
  if (category.includes('产品设计') || category.includes('product')) {
    return DocumentLevel.PRODUCT;
  }
  if (category.includes('技术') || category.includes('technical') || category.includes('开发')) {
    return DocumentLevel.DEVELOPER;
  }
  if (category.includes('用户') || category.includes('user') || category.includes('支持') || category.includes('support')) {
    return DocumentLevel.USER;
  }
  if (category.includes('运维') || category.includes('operations') || category.includes('安全') || category.includes('security')) {
    return DocumentLevel.OPERATIONS;
  }
  
  // Default to cross-level
  return DocumentLevel.CROSS_LEVEL;
}

// Document-specific icons (more specific than level icons)
const DOCUMENT_ICONS: Record<string, string> = {
  // Strategic Level
  'requirements': '📋',
  'requirements_analyst': '📋',
  'project_charter': '📜',
  'business_model': '💼',
  'marketing_plan': '📢',
  'gtm_strategy': '🎯',
  'stakeholders_doc': '👥',
  'stakeholder_communication': '💬',
  'risk_management_plan': '⚠️',
  'change_management_plan': '🔄',
  'feature_roadmap': '🗺️',
  
  // Product Level
  'user_stories': '📖',
  'prd': '📝',
  'fsd': '📐',
  'pm_documentation': '📊',
  'user_analytics': '📈',
  'dashboard_metrics': '📉',
  'kpi_metrics_doc': '🎯',
  'release_notes': '🚀',
  'user_feedback_plan': '💭',
  'ab_testing_docs': '🧪',
  'onboarding_flow': '🎓',
  'interaction_flows': '🔄',
  'ui_mockups': '🎨',
  'ui_style_guide': '🎨',
  
  // Developer Level
  'technical_documentation': '💻',
  'tad': '📐',
  'api_documentation': '🔌',
  'database_schema': '🗄️',
  'developer_guide': '👨‍💻',
  'developer_documentation': '👨‍💻',
  'setup_guide': '⚙️',
  'test_plan': '🧪',
  'test_documentation': '✅',
  'cicd_doc': '🔄',
  'api_versioning_policy': '📌',
  'configuration_management_plan': '⚙️',
  'deployment_plan': '🚀',
  'scalability_plan': '📈',
  'technical_debt_log': '📝',
  'third_party_integrations': '🔗',
  'feature_flag_docs': '🚩',
  
  // User Level
  'user_documentation': '📚',
  'user_support_doc': '🆘',
  'knowledge_base': '📖',
  'support_training_doc': '🎓',
  
  // Operations Level
  'backup_recovery_plan': '💾',
  'maintenance_plan': '🔧',
  'monitoring_logging_plan': '📊',
  'performance_optimization_doc': '⚡',
  'cloud_infrastructure_doc': '☁️',
  'bcp': '🛡️',
  'sla': '📋',
  'vendor_management_docs': '🤝',
  'incident_response_plan': '🚨',
  'data_retention_policy': '📦',
  'data_governance_policy': '📜',
  'security_plan': '🔒',
  'privacy_policy': '🔐',
  'terms_of_service': '📄',
  'legal_compliance': '⚖️',
  'accessibility_plan': '♿',
  'eol_policy': '⏰',
  'localization_plan': '🌍',
  'technical_audit': '🔍',
  
  // Cross-Level
  'support_playbook': '📘',
  'quality_review': '⭐',
  'document_improver': '✨',
  'format_converter': '🔄',
  'code_analyst': '🔬',
};

/**
 * Get document icon from document ID
 * Returns document-specific icon if available, otherwise falls back to level icon
 */
export function getDocumentIcon(docId: string): string {
  // Try document-specific icon first
  if (docId in DOCUMENT_ICONS) {
    return DOCUMENT_ICONS[docId];
  }
  
  // Try normalized match (handle variations like requirements_analyst vs requirements)
  const normalized = docId.toLowerCase().replace(/[_-]/g, '');
  for (const [key, icon] of Object.entries(DOCUMENT_ICONS)) {
    if (key.toLowerCase().replace(/[_-]/g, '') === normalized) {
      return icon;
    }
  }
  
  // Fall back to level icon
  const level = getDocumentLevel(docId);
  return LEVEL_ICONS[level];
}

/**
 * Rank documents by strategic level (Level 1 -> Level 5)
 */
export function rankDocuments(documents: DocumentTemplate[]): DocumentTemplate[] {
  return [...documents].sort((a, b) => {
    const levelA = getDocumentLevel(a);
    const levelB = getDocumentLevel(b);
    
    // Sort by level first (1-5, then 0 for cross-level)
    if (levelA !== levelB) {
      // Cross-level goes to the end
      if (levelA === DocumentLevel.CROSS_LEVEL) return 1;
      if (levelB === DocumentLevel.CROSS_LEVEL) return -1;
      return levelA - levelB;
    }
    
    // Within same level, sort by priority
    const priorityWeight: Record<string, number> = {
      '高': 3, 'High': 3,
      '中': 2, 'Medium': 2,
      '低': 1, 'Low': 1,
      '': 0,
    };
    const priorityA = priorityWeight[a.priority || ''] || 0;
    const priorityB = priorityWeight[b.priority || ''] || 0;
    
    if (priorityB !== priorityA) {
      return priorityB - priorityA;
    }
    
    // Finally, sort by name
    return a.name.localeCompare(b.name);
  });
}

/**
 * Filter documents by view mode (team/solo/all)
 */
export function filterDocumentsByView(
  documents: DocumentTemplate[],
  viewMode: ViewMode
): DocumentTemplate[] {
  if (viewMode === 'all') {
    return documents;
  }

  return documents.filter((doc) => {
    const audience = doc.audience || '';
    
    if (viewMode === 'team') {
      // Team view: show documents for team or mixed audience
      return audience.includes('团队') || 
             audience.includes('Team') || 
             audience.includes('混合') || 
             audience.includes('Mixed');
    } else if (viewMode === 'solo') {
      // Solo view: show documents for personal/solo or mixed audience
      return audience.includes('个人') || 
             audience.includes('Solo') || 
             audience.includes('Personal') ||
             audience.includes('混合') || 
             audience.includes('Mixed');
    }

    return true;
  });
}

/**
 * Organize documents by strategic level
 */
export function organizeByLevel(documents: DocumentTemplate[]): {
  strategic: DocumentTemplate[];
  product: DocumentTemplate[];
  developer: DocumentTemplate[];
  user: DocumentTemplate[];
  operations: DocumentTemplate[];
  crossLevel: DocumentTemplate[];
} {
  const strategic: DocumentTemplate[] = [];
  const product: DocumentTemplate[] = [];
  const developer: DocumentTemplate[] = [];
  const user: DocumentTemplate[] = [];
  const operations: DocumentTemplate[] = [];
  const crossLevel: DocumentTemplate[] = [];
  
  documents.forEach((doc) => {
    const level = getDocumentLevel(doc);
    switch (level) {
      case DocumentLevel.STRATEGIC:
        strategic.push(doc);
        break;
      case DocumentLevel.PRODUCT:
        product.push(doc);
        break;
      case DocumentLevel.DEVELOPER:
        developer.push(doc);
        break;
      case DocumentLevel.USER:
        user.push(doc);
        break;
      case DocumentLevel.OPERATIONS:
        operations.push(doc);
        break;
      case DocumentLevel.CROSS_LEVEL:
        crossLevel.push(doc);
        break;
    }
  });
  
  return { strategic, product, developer, user, operations, crossLevel };
}

/**
 * Organize documents by category
 */
export function organizeByCategory(documents: DocumentTemplate[]): {
  [category: string]: DocumentTemplate[];
} {
  const organized: { [category: string]: DocumentTemplate[] } = {};
  
  documents.forEach((doc) => {
    const category = doc.category || '未分类 / Uncategorized';
    if (!organized[category]) {
      organized[category] = [];
    }
    organized[category].push(doc);
  });
  
  // Sort documents within each category by priority and name
  Object.keys(organized).forEach((category) => {
    organized[category].sort((a, b) => {
      const priorityWeight: Record<string, number> = {
        '高': 3, 'High': 3,
        '中': 2, 'Medium': 2,
        '低': 1, 'Low': 1,
        '': 0,
      };
      const priorityA = priorityWeight[a.priority || ''] || 0;
      const priorityB = priorityWeight[b.priority || ''] || 0;
      
      if (priorityB !== priorityA) {
        return priorityB - priorityA;
      }
      
      return a.name.localeCompare(b.name);
    });
  });
  
  return organized;
}

/**
 * Get recommended documents based on dependencies
 * When a document is selected, recommend its dependencies
 */
export function getRecommendedDocuments(
  selectedDocId: string,
  allDocuments: DocumentTemplate[]
): DocumentTemplate[] {
  const selectedDoc = allDocuments.find((d) => d.id === selectedDocId);
  if (!selectedDoc || !selectedDoc.dependencies || selectedDoc.dependencies.length === 0) {
    return [];
  }
  
  return selectedDoc.dependencies
    .map((depId) => allDocuments.find((d) => d.id === depId))
    .filter((doc): doc is DocumentTemplate => doc !== undefined);
}
