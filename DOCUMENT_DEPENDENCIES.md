# Document Dependencies

This document lists all document dependencies based on the code configuration in `config/document_definitions.json`.

Generated from: `config/document_definitions.json`

---

## Summary

- **Total Documents**: 59
- **Documents with Dependencies**: 55
- **Documents without Dependencies**: 4

---

## 产品设计 / 功能

### FSD (Functional Spec Doc) (`fsd`)

- **Priority**: 高
- **Owner**: Product Manager / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 功能实现细节

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `tad` - TAD (Technical Architecture Doc)

---

### Interaction / Flow Diagrams (`interaction_flows`)

- **Priority**: 中
- **Owner**: UX/UI Designer / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 用户流程、系统交互

**Dependencies** (2):

  - `ui_mockups` - UI Mockups / Mockups Docs
  - `fsd` - FSD (Functional Spec Doc)

---

### Onboarding Flow (`onboarding_flow`)

- **Priority**: 高
- **Owner**: UX/UI Designer / PM
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 用户注册、初次使用流程

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `ui_mockups` - UI Mockups / Mockups Docs

---

### PRD (Product Requirements Doc) (`prd`)

- **Priority**: 高
- **Owner**: Product Manager
- **Stage**: MVP
- **Description**: 产品功能详细说明

**Dependencies** (2):

  - `requirements` - Requirements Document
  - `feature_roadmap` - Feature Roadmap

---

### TAD (Technical Architecture Doc) (`tad`)

- **Priority**: 高
- **Owner**: Tech Lead / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 技术架构设计

**Dependencies** (2):

  - `database_schema` - Database Schema
  - `api_documentation` - API Documentation

---

### UI Mockups / Mockups Docs (`ui_mockups`)

- **Priority**: 高
- **Owner**: UX/UI Designer
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 页面设计和布局

**Dependencies** (1):

  - `prd` - PRD (Product Requirements Doc)

---

### UI Style Guide (`ui_style_guide`)

- **Priority**: 中
- **Owner**: UX/UI Designer
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 颜色、字体、组件规范

**Dependencies** (1):

  - `ui_mockups` - UI Mockups / Mockups Docs

---

## 安全 / 合规

### Accessibility Plan / ADA Compliance (`accessibility_plan`)

- **Priority**: 中
- **Owner**: UX/UI Designer / PM
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 无障碍功能设计

**Dependencies** (2):

  - `ui_style_guide` - UI Style Guide
  - `ui_mockups` - UI Mockups / Mockups Docs

---

### Data Retention & Archiving Policy (`data_retention_policy`)

- **Priority**: 高
- **Owner**: PM / DevOps
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 数据保留与归档

**Dependencies** (1):

  - `database_schema` - Database Schema

---

### End-of-Life (EOL) Policy (`eol_policy`)

- **Priority**: 中
- **Owner**: PM / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 产品或功能退役策略

**Dependencies** (2):

  - `feature_roadmap` - Feature Roadmap
  - `api_versioning_policy` - API Versioning & Deprecation Policy

---

### Incident Response Plan (`incident_response_plan`)

- **Priority**: 高
- **Owner**: Security Lead / DevOps
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 安全/系统事件响应

**Dependencies** (2):

  - `security_plan` - Security Plan
  - `monitoring_logging_plan` - Monitoring & Logging Plan

---

### Legal / Terms of Service (ToS) (`terms_of_service`)

- **Priority**: 高
- **Owner**: Legal
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 用户协议与法律条款

**Dependencies** (1):

  - `privacy_policy` - Privacy Policy / GDPR Compliance

---

### Localization / Internationalization Plan (`localization_plan`)

- **Priority**: 中
- **Owner**: UX/UI Designer / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 多语言支持策略

**Dependencies** (2):

  - `ui_mockups` - UI Mockups / Mockups Docs
  - `prd` - PRD (Product Requirements Doc)

---

### Privacy Policy / GDPR Compliance (`privacy_policy`)

- **Priority**: 高
- **Owner**: Legal / PM
- **Stage**: MVP
- **Description**: 用户隐私及法规合规

**Dependencies** (1):

  - `security_plan` - Security Plan

---

### Security Plan (`security_plan`)

- **Priority**: 高
- **Owner**: Security Lead / DevOps
- **Stage**: MVP
- **Description**: 系统安全策略

**Dependencies** (2):

  - `tad` - TAD (Technical Architecture Doc)
  - `cicd_doc` - CI/CD Pipeline Doc

---

## 技术 / 开发

### API Documentation (`api_documentation`)

- **Priority**: 高
- **Owner**: Backend Dev
- **Stage**: MVP
- **Description**: API接口说明

**Dependencies**: None (root document)

---

### API Versioning & Deprecation Policy (`api_versioning_policy`)

- **Priority**: 中
- **Owner**: Backend Dev / Tech Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: API升级与退役策略

**Dependencies** (1):

  - `api_documentation` - API Documentation

---

### CI/CD Pipeline Doc (`cicd_doc`)

- **Priority**: 中
- **Owner**: DevOps
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 持续集成/部署流程

**Dependencies** (2):

  - `developer_guide` - Developer Guide / README
  - `tad` - TAD (Technical Architecture Doc)

---

### Configuration Management Plan (`configuration_management_plan`)

- **Priority**: 中
- **Owner**: DevOps / Tech Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 系统配置与版本管理

**Dependencies** (2):

  - `developer_guide` - Developer Guide / README
  - `cicd_doc` - CI/CD Pipeline Doc

---

### Database Schema (`database_schema`)

- **Priority**: 高
- **Owner**: Backend Dev / DB Admin
- **Stage**: MVP
- **Description**: 数据库设计

**Dependencies**: None (root document)

---

### Deployment Plan (`deployment_plan`)

- **Priority**: 中
- **Owner**: DevOps / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 上线与发布计划

**Dependencies** (2):

  - `cicd_doc` - CI/CD Pipeline Doc
  - `tad` - TAD (Technical Architecture Doc)

---

### Developer Guide / README (`developer_guide`)

- **Priority**: 高
- **Owner**: Dev Lead
- **Stage**: MVP
- **Description**: 开发指南和依赖说明

**Dependencies** (2):

  - `api_documentation` - API Documentation
  - `database_schema` - Database Schema

---

### Monitoring & Logging Plan (`monitoring_logging_plan`)

- **Priority**: 高
- **Owner**: DevOps / QA
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 系统监控和日志策略

**Dependencies** (2):

  - `tad` - TAD (Technical Architecture Doc)
  - `cicd_doc` - CI/CD Pipeline Doc

---

### Scalability Plan (`scalability_plan`)

- **Priority**: 中
- **Owner**: Tech Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 系统扩展方案

**Dependencies** (1):

  - `tad` - TAD (Technical Architecture Doc)

---

### Technical Debt Log / Refactoring Plan (`technical_debt_log`)

- **Priority**: 中
- **Owner**: Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 技术欠债记录

**Dependencies** (2):

  - `tad` - TAD (Technical Architecture Doc)
  - `fsd` - FSD (Functional Spec Doc)

---

## 测试 / QA / 支持

### Experimentation / A/B Testing Docs (`ab_testing_docs`)

- **Priority**: 中
- **Owner**: Product Manager / Data Analyst
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 功能优化实验设计

**Dependencies** (2):

  - `feature_roadmap` - Feature Roadmap
  - `prd` - PRD (Product Requirements Doc)

---

### Knowledge Base (`knowledge_base`)

- **Priority**: 中
- **Owner**: Support Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 常见问题和帮助文档

**Dependencies**: None (root document)

---

### Support Playbook (`support_playbook`)

- **Priority**: 高
- **Owner**: Support Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 客服处理流程

**Dependencies** (2):

  - `user_support_doc` - User Support Document
  - `test_plan` - Test Plan Document

---

### Support Team Training Document (`support_training_doc`)

- **Priority**: 中
- **Owner**: Support Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 客服培训材料

**Dependencies** (2):

  - `support_playbook` - Support Playbook
  - `user_support_doc` - User Support Document

---

### Test Plan Document (`test_plan`)

- **Priority**: 高
- **Owner**: QA
- **Stage**: MVP
- **Description**: 测试用例、方法和流程

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `fsd` - FSD (Functional Spec Doc)

---

### User Feedback Plan (`user_feedback_plan`)

- **Priority**: 高
- **Owner**: Product Manager / UX
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 用户反馈收集与分析

**Dependencies** (2):

  - `knowledge_base` - Knowledge Base
  - `test_plan` - Test Plan Document

---

### User Support Document (`user_support_doc`)

- **Priority**: 高
- **Owner**: Support Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 用户支持指南

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `knowledge_base` - Knowledge Base

---

## 用户 / 产品分析

### Dashboard Metrics Specification (`dashboard_metrics`)

- **Priority**: 高
- **Owner**: UX/UI Designer / Data Analyst
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 仪表盘数据指标

**Dependencies** (1):

  - `kpi_metrics_doc` - KPIs / Metrics Document

---

### Go-To-Market (GTM) Strategy (`gtm_strategy`)

- **Priority**: 中
- **Owner**: Product Manager / Marketing
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 上市推广策略

**Dependencies** (2):

  - `feature_roadmap` - Feature Roadmap
  - `business_model` - Business Model

---

### KPIs / Metrics Document (`kpi_metrics_doc`)

- **Priority**: 高
- **Owner**: Product Manager / Data Analyst
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 产品指标和分析方法

**Dependencies** (1):

  - `feature_roadmap` - Feature Roadmap

---

### Release Notes / Version History (`release_notes`)

- **Priority**: 高
- **Owner**: Product Manager / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 版本功能更新与修复记录

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `fsd` - FSD (Functional Spec Doc)

---

### Third-Party Integration Documentation (`third_party_integrations`)

- **Priority**: 高
- **Owner**: Dev Lead / Backend Dev
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 第三方服务集成说明

**Dependencies** (2):

  - `api_documentation` - API Documentation
  - `tad` - TAD (Technical Architecture Doc)

---

### User Analytics / Behavior Tracking Doc (`user_analytics`)

- **Priority**: 中
- **Owner**: Data Analyst / PM
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 用户行为数据分析方法

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `dashboard_metrics` - Dashboard Metrics Specification

---

## 运维 / 高级管理

### Backup & Recovery Plan (`backup_recovery_plan`)

- **Priority**: 高
- **Owner**: DevOps
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 数据备份与恢复流程

**Dependencies** (2):

  - `database_schema` - Database Schema
  - `configuration_management_plan` - Configuration Management Plan

---

### Business Continuity Plan (BCP) (`bcp`)

- **Priority**: 中
- **Owner**: PM / DevOps
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 灾难或停机业务连续性

**Dependencies** (2):

  - `risk_management_plan` - Risk Management / Mitigation Plan
  - `backup_recovery_plan` - Backup & Recovery Plan

---

### Cloud Infrastructure / Cost Management Doc (`cloud_infrastructure_doc`)

- **Priority**: 中
- **Owner**: DevOps / Tech Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 云资源架构及成本优化

**Dependencies** (2):

  - `tad` - TAD (Technical Architecture Doc)
  - `scalability_plan` - Scalability Plan

---

### Maintenance Plan (`maintenance_plan`)

- **Priority**: 高
- **Owner**: DevOps
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 系统维护流程

**Dependencies** (2):

  - `cicd_doc` - CI/CD Pipeline Doc
  - `monitoring_logging_plan` - Monitoring & Logging Plan

---

### Performance Tuning & Optimization Doc (`performance_optimization_doc`)

- **Priority**: 中
- **Owner**: DevOps / Tech Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 性能优化方案

**Dependencies** (2):

  - `tad` - TAD (Technical Architecture Doc)
  - `monitoring_logging_plan` - Monitoring & Logging Plan

---

### SLA / Service Level Agreement (`sla`)

- **Priority**: 中
- **Owner**: PM / Legal
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 可用性和支持承诺

**Dependencies** (2):

  - `business_model` - Business Model
  - `maintenance_plan` - Maintenance Plan

---

### Vendor / Supplier Management Docs (`vendor_management_docs`)

- **Priority**: 中
- **Owner**: PM / Legal
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 第三方服务与合同管理

**Dependencies** (2):

  - `sla` - SLA / Service Level Agreement
  - `bcp` - Business Continuity Plan (BCP)

---

## 项目管理 / 规划

### Business Model (`business_model`)

- **Priority**: 高
- **Owner**: Product Manager / CEO
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 商业模式、盈利策略

**Dependencies** (1):

  - `market_research` - Market Research & Competitive Analysis

---

### Change Management Plan (`change_management_plan`)

- **Priority**: 中
- **Owner**: Product Manager / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 功能或架构变更流程

**Dependencies** (2):

  - `pm_management_doc` - PM Management Doc
  - `feature_roadmap` - Feature Roadmap

---

### Feature Roadmap (`feature_roadmap`)

- **Priority**: 高
- **Owner**: Product Manager
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 功能迭代计划

**Dependencies** (3):

  - `requirements` - Requirements Document
  - `project_charter` - Project Charter
  - `business_model` - Business Model

---

### PM Management Doc (`pm_management_doc`)

- **Priority**: 高
- **Owner**: Product Manager
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 项目管理流程、职责分工

**Dependencies** (2):

  - `project_charter` - Project Charter
  - `stakeholders_doc` - Stakeholders Document

---

### Project Charter (`project_charter`)

- **Priority**: 高
- **Owner**: Product Manager
- **Stage**: MVP
- **Description**: 产品目标、范围、里程碑

**Dependencies** (3):

  - `stakeholders_doc` - Stakeholders Document
  - `market_research` - Market Research & Competitive Analysis
  - `business_model` - Business Model

---

### Requirements Document (`requirements`)

- **Priority**: 高
- **Owner**: Product Manager / BA
- **Stage**: MVP
- **Description**: 系统功能和需求说明

**Dependencies** (3):

  - `business_model` - Business Model
  - `market_research` - Market Research & Competitive Analysis
  - `project_charter` - Project Charter

---

### Risk Management / Mitigation Plan (`risk_management_plan`)

- **Priority**: 中
- **Owner**: PM / QA / Dev Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 风险分析与缓解措施

**Dependencies** (3):

  - `project_charter` - Project Charter
  - `requirements` - Requirements Document
  - `business_model` - Business Model

---

### Stakeholders Document (`stakeholders_doc`)

- **Priority**: 中
- **Owner**: Product Manager
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 利益相关方列表及角色

**Dependencies** (1):

  - `business_model` - Business Model

---

### Work Breakdown Structure (WBS) (`wbs`)

- **Priority**: 高
- **Owner**: PM / Product Manager
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 任务拆分、进度计划

**Dependencies** (3):

  - `project_charter` - Project Charter
  - `feature_roadmap` - Feature Roadmap
  - `requirements` - Requirements Document

---

## 高级 / 可选 / 补充

### Data Governance / Data Quality Policy (`data_governance_policy`)

- **Priority**: 中
- **Owner**: Data Analyst / PM
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 数据标准化、准确性、完整性

**Dependencies** (2):

  - `database_schema` - Database Schema
  - `user_analytics` - User Analytics / Behavior Tracking Doc

---

### Experimentation / Feature Flag Docs (`feature_flag_docs`)

- **Priority**: 中
- **Owner**: Dev Lead / PM
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 功能实验和开关管理

**Dependencies** (2):

  - `prd` - PRD (Product Requirements Doc)
  - `ab_testing_docs` - Experimentation / A/B Testing Docs

---

### Innovation / R&D Plan (`innovation_plan`)

- **Priority**: 中
- **Owner**: Product Manager / Tech Lead
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 新功能或技术探索路线

**Dependencies** (2):

  - `feature_roadmap` - Feature Roadmap
  - `technical_audit` - Technical Audit / Compliance Audit Reports

---

### Market Research & Competitive Analysis (`market_research`)

- **Priority**: 中
- **Owner**: Product Manager / Marketing
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 市场和竞品分析

**Dependencies**: None (root document)

---

### Technical Audit / Compliance Audit Reports (`technical_audit`)

- **Priority**: 中
- **Owner**: Security Lead / Legal
- **Stage**: 产品成熟 / 后续迭代
- **Description**: 技术与合规审计

**Dependencies** (2):

  - `security_plan` - Security Plan
  - `privacy_policy` - Privacy Policy / GDPR Compliance

---

## Dependency Graph (Text Format)

This section shows the dependency relationships in a hierarchical format.

### Root Documents (No Dependencies)

- `api_documentation` - API Documentation
- `database_schema` - Database Schema
- `knowledge_base` - Knowledge Base
- `market_research` - Market Research & Competitive Analysis

### Dependency Chains

**API Documentation** (`api_documentation`) is depended upon by:
  - `api_versioning_policy` - API Versioning & Deprecation Policy
  - `developer_guide` - Developer Guide / README
  - `tad` - TAD (Technical Architecture Doc)
  - `third_party_integrations` - Third-Party Integration Documentation

**Database Schema** (`database_schema`) is depended upon by:
  - `backup_recovery_plan` - Backup & Recovery Plan
  - `data_governance_policy` - Data Governance / Data Quality Policy
  - `data_retention_policy` - Data Retention & Archiving Policy
  - `developer_guide` - Developer Guide / README
  - `tad` - TAD (Technical Architecture Doc)

**Knowledge Base** (`knowledge_base`) is depended upon by:
  - `user_feedback_plan` - User Feedback Plan
  - `user_support_doc` - User Support Document

**Market Research & Competitive Analysis** (`market_research`) is depended upon by:
  - `business_model` - Business Model
  - `project_charter` - Project Charter
  - `requirements` - Requirements Document

## Complete Dependency List

This section lists all documents with their direct dependencies.

- **API Documentation** (`api_documentation`) → *no dependencies*
- **API Versioning & Deprecation Policy** (`api_versioning_policy`) → `api_documentation`
- **Accessibility Plan / ADA Compliance** (`accessibility_plan`) → `ui_style_guide`, `ui_mockups`
- **Backup & Recovery Plan** (`backup_recovery_plan`) → `database_schema`, `configuration_management_plan`
- **Business Continuity Plan (BCP)** (`bcp`) → `risk_management_plan`, `backup_recovery_plan`
- **Business Model** (`business_model`) → `market_research`
- **CI/CD Pipeline Doc** (`cicd_doc`) → `developer_guide`, `tad`
- **Change Management Plan** (`change_management_plan`) → `pm_management_doc`, `feature_roadmap`
- **Cloud Infrastructure / Cost Management Doc** (`cloud_infrastructure_doc`) → `tad`, `scalability_plan`
- **Configuration Management Plan** (`configuration_management_plan`) → `developer_guide`, `cicd_doc`
- **Dashboard Metrics Specification** (`dashboard_metrics`) → `kpi_metrics_doc`
- **Data Governance / Data Quality Policy** (`data_governance_policy`) → `database_schema`, `user_analytics`
- **Data Retention & Archiving Policy** (`data_retention_policy`) → `database_schema`
- **Database Schema** (`database_schema`) → *no dependencies*
- **Deployment Plan** (`deployment_plan`) → `cicd_doc`, `tad`
- **Developer Guide / README** (`developer_guide`) → `api_documentation`, `database_schema`
- **End-of-Life (EOL) Policy** (`eol_policy`) → `feature_roadmap`, `api_versioning_policy`
- **Experimentation / A/B Testing Docs** (`ab_testing_docs`) → `feature_roadmap`, `prd`
- **Experimentation / Feature Flag Docs** (`feature_flag_docs`) → `prd`, `ab_testing_docs`
- **FSD (Functional Spec Doc)** (`fsd`) → `prd`, `tad`
- **Feature Roadmap** (`feature_roadmap`) → `requirements`, `project_charter`, `business_model`
- **Go-To-Market (GTM) Strategy** (`gtm_strategy`) → `feature_roadmap`, `business_model`
- **Incident Response Plan** (`incident_response_plan`) → `security_plan`, `monitoring_logging_plan`
- **Innovation / R&D Plan** (`innovation_plan`) → `feature_roadmap`, `technical_audit`
- **Interaction / Flow Diagrams** (`interaction_flows`) → `ui_mockups`, `fsd`
- **KPIs / Metrics Document** (`kpi_metrics_doc`) → `feature_roadmap`
- **Knowledge Base** (`knowledge_base`) → *no dependencies*
- **Legal / Terms of Service (ToS)** (`terms_of_service`) → `privacy_policy`
- **Localization / Internationalization Plan** (`localization_plan`) → `ui_mockups`, `prd`
- **Maintenance Plan** (`maintenance_plan`) → `cicd_doc`, `monitoring_logging_plan`
- **Market Research & Competitive Analysis** (`market_research`) → *no dependencies*
- **Monitoring & Logging Plan** (`monitoring_logging_plan`) → `tad`, `cicd_doc`
- **Onboarding Flow** (`onboarding_flow`) → `prd`, `ui_mockups`
- **PM Management Doc** (`pm_management_doc`) → `project_charter`, `stakeholders_doc`
- **PRD (Product Requirements Doc)** (`prd`) → `requirements`, `feature_roadmap`
- **Performance Tuning & Optimization Doc** (`performance_optimization_doc`) → `tad`, `monitoring_logging_plan`
- **Privacy Policy / GDPR Compliance** (`privacy_policy`) → `security_plan`
- **Project Charter** (`project_charter`) → `stakeholders_doc`, `market_research`, `business_model`
- **Release Notes / Version History** (`release_notes`) → `prd`, `fsd`
- **Requirements Document** (`requirements`) → `business_model`, `market_research`, `project_charter`
- **Risk Management / Mitigation Plan** (`risk_management_plan`) → `project_charter`, `requirements`, `business_model`
- **SLA / Service Level Agreement** (`sla`) → `business_model`, `maintenance_plan`
- **Scalability Plan** (`scalability_plan`) → `tad`
- **Security Plan** (`security_plan`) → `tad`, `cicd_doc`
- **Stakeholders Document** (`stakeholders_doc`) → `business_model`
- **Support Playbook** (`support_playbook`) → `user_support_doc`, `test_plan`
- **Support Team Training Document** (`support_training_doc`) → `support_playbook`, `user_support_doc`
- **TAD (Technical Architecture Doc)** (`tad`) → `database_schema`, `api_documentation`
- **Technical Audit / Compliance Audit Reports** (`technical_audit`) → `security_plan`, `privacy_policy`
- **Technical Debt Log / Refactoring Plan** (`technical_debt_log`) → `tad`, `fsd`
- **Test Plan Document** (`test_plan`) → `prd`, `fsd`
- **Third-Party Integration Documentation** (`third_party_integrations`) → `api_documentation`, `tad`
- **UI Mockups / Mockups Docs** (`ui_mockups`) → `prd`
- **UI Style Guide** (`ui_style_guide`) → `ui_mockups`
- **User Analytics / Behavior Tracking Doc** (`user_analytics`) → `prd`, `dashboard_metrics`
- **User Feedback Plan** (`user_feedback_plan`) → `knowledge_base`, `test_plan`
- **User Support Document** (`user_support_doc`) → `prd`, `knowledge_base`
- **Vendor / Supplier Management Docs** (`vendor_management_docs`) → `sla`, `bcp`
- **Work Breakdown Structure (WBS)** (`wbs`) → `project_charter`, `feature_roadmap`, `requirements`
