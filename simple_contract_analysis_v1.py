import os
import google.generativeai as genai
from typing import List, Optional
from datetime import date, datetime
import logging
from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_ai import Agent


class AddressDetail(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class PartyDetail(BaseModel):
    name: str = Field(..., description="Full legal name of the party", repr=True)
    role: Optional[str] = Field(None, description="e.g., Licensor, Licensee, Vendor, Client, Party A, Party B")
    address: Optional[AddressDetail] = Field(None, description="Physical or mailing address",repr=False) # repr=False to avoid showing the address in the log (or in the final output)
    authorized_signatory_name: Optional[str] = Field(None, description="Name of the person who signed, if identifiable")
    full_text_reference: Optional[str] = Field(None, description="Exact text identifying this party") # Optional: useful for traceability

class SoftwareProductDetail(BaseModel):
    name: str = Field(..., description="Primary name of the software or product")
    version: Optional[str] = Field(None, description="Specific version identifier, if mentioned")
    modules_features: Optional[List[str]] = Field(default_factory=list, description="List of included modules or key features")
    description: Optional[str] = Field(None, description="Brief description of the software/product")

class ServiceDetail(BaseModel):
    service_type: str = Field(..., description="Type of service provided, e.g., Maintenance, Support, Training, Integration")
    description: Optional[str] = Field(None, description="Details about the service scope")

class PaymentMilestoneDetail(BaseModel):
    description: str = Field(..., description="What triggers or describes this payment")
    amount: Optional[float] = Field(None, description="Monetary amount")
    currency: Optional[str] = Field(None, description="Currency code (e.g., USD, EUR, INR)")
    due_date_description: Optional[str] = Field(None, description="When the payment is due (e.g., 'Net 30', 'Upon signing', specific date)")
    due_date: Optional[date] = Field(None, description="Specific calendar due date, if available")


class PenaltyDetail(BaseModel):
    condition: str = Field(..., description="Condition triggering the penalty (e.g., Late Payment, Non-performance)")
    penalty_description: str = Field(..., description="Description of the penalty (e.g., '1.5% interest per month', 'Fixed fee')")

class SLADetail(BaseModel):
    metric: str = Field(..., description="The SLA metric (e.g., Uptime, Response Time, Resolution Time)")
    commitment: str = Field(..., description="The specific commitment (e.g., '99.9% uptime', '4 hours for critical issues')")
    remedy: Optional[str] = Field(None, description="Remedy or credit for failing to meet the SLA")

class DeliverableDetail(BaseModel):
    description: str = Field(..., description="Description of the deliverable item or milestone")
    due_date_description: Optional[str] = Field(None, description="When it's due (e.g., 'Phase 1 complete', specific date)")
    due_date: Optional[date] = Field(None, description="Specific calendar due date, if available")
    acceptance_criteria_summary: Optional[str] = Field(None, description="Brief summary of how the deliverable is accepted")

class ContractAnalysisResult(BaseModel):
    """Simplified structure for debugging extraction from a contract document."""

    # 1. Basic Metadata (Keep a few simple ones)
    contract_title: Optional[str] = Field(None, description="The main title of the contract document, if present.")
    effective_date: Optional[date] = Field(None, description="The date the contract becomes legally effective.")
    expiration_date: Optional[date] = Field(None, description="The date the contract term ends, if specified.") # Commented out
    execution_date: Optional[date] = Field(None, description="The date the contract was signed by the parties.") # Commented out
    contract_id_reference: Optional[str] = Field(None, description="Any unique identifier or reference number for the contract.") # Commented out

    # # 2. Party Information (COMMENTED OUT - Includes List[PartyDetail])
    # parties: List[PartyDetail] = Field(default_factory=list, description="List of all identified parties involved in the contract.")

    # # 3. Contract Subject & Scope (COMMENTED OUT - Includes List[SoftwareProductDetail] and List[ServiceDetail])
    primary_software_products: List[SoftwareProductDetail] = Field(default_factory=list, description="Details of the main software/products being licensed or sold.")
    included_services: List[ServiceDetail] = Field(default_factory=list, description="Details of services included (e.g., maintenance, support, training).")
    intended_use_case_purpose: Optional[str] = Field(None, description="The stated purpose or intended use of the software/service, if mentioned.") # Keep one simple string

    # # 4. Commercial Terms (COMMENTED OUT - Includes List fields)
    total_contract_value_description: Optional[str] = Field(None, description="Text describing the total financial value or pricing structure (e.g., '$50,000 USD', 'See Schedule B').")
    payment_milestones: List[PaymentMilestoneDetail] = Field(default_factory=list, description="Breakdown of payment amounts, schedules, and currencies.")
    penalty_clauses: List[PenaltyDetail] = Field(default_factory=list, description="Specific penalties mentioned (e.g., for late payment, non-compliance).")
    discounts_credits_description: Optional[str] = Field(None, description="Mention of any discounts or credits offered.")

    # 5. Licensing Terms (Keep simple fields, comment out lists if any)
    license_type_description: Optional[str] = Field(None, description="Description of the license grant (e.g., Perpetual, Subscription, SaaS, Term-based).")
    usage_limits_description: Optional[str] = Field(None, description="Description of limits on users, devices, cores, etc.")
    territory_description: Optional[str] = Field(None, description="Geographic scope where the license is valid (e.g., Worldwide, North America, India).")
    transferability_sublicensing_allowed: Optional[bool] = Field(None, description="Is transferring or sub-licensing the license permitted?") # Keep bool

    # 6. Service Level Commitments (SLAs) (COMMENTED OUT - Includes List[SLADetail])
    support_hours_availability: Optional[str] = Field(None, description="Stated hours or availability of support (e.g., '9-5 EST', '24/7').")
    service_level_agreements: List[SLADetail] = Field(default_factory=list, description="Specific, measurable SLA commitments (e.g., response times, uptime).")
    maintenance_schedule_description: Optional[str] = Field(None, description="Information regarding scheduled maintenance windows or procedures.")

    # 8. Deliverables & Timelines (COMMENTED OUT - Includes List[DeliverableDetail])
    key_deliverables: List[DeliverableDetail] = Field(default_factory=list, description="Specific items or milestones to be delivered under the contract.")

    # # 9. Risk & Compliance Flags (Keep simple fields, comment out lists)
    insurance_requirements_description: Optional[str] = Field(None, description="Description of any required insurance coverage levels or types.")
    data_privacy_clause_summary: Optional[str] = Field(None, description="Summary of clauses related to data protection, GDPR, CCPA, HIPAA, etc.")
    ip_ownership_description: Optional[str] = Field(None, description="Statement regarding ownership of intellectual property created or licensed.")

    @field_validator('effective_date') # Removed 'expiration_date', 'execution_date'
    def check_date_logic(cls, v, info):
        if isinstance(v, date):
            pass
        return v


# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logging.warning("GOOGLE_API_KEY environment variable not found...")

contract_text= """ MASTER SOFTWARE LICENSE AND SERVICES AGREEMENT - Ref: MSSA-2024-TS-SL

This Master Software License and Services Agreement ("Agreement") is effective as of July 15, 2024 ("Effective Date"), and executed on July 10, 2024 ("Execution Date"), by and between Quantum Dynamics Inc., a Delaware corporation with offices at 1 Quantum Leap, Palo Alto, CA 94301 ("Quantum"), and Global Synergy Partners LLC, a New York limited liability company with its principal place of business at 789 World Ave, New York, NY 10001 ("Synergy").

RECITALS
A. Quantum develops and licenses proprietary software known as "FusionPlatform" version 3.0, including modules "DataCore" and "AnalyticsSuite".
B. Synergy wishes to license FusionPlatform and receive related support services for use in automating financial data analytics and reporting workflows across their global operations.

AGREEMENT

LICENSE GRANT. Quantum grants Synergy a non-exclusive, worldwide, 3-year subscription license to use FusionPlatform v3.0 (DataCore & AnalyticsSuite modules) for up to 250 named users solely for Synergy's internal business operations. The license is for SaaS deployment only and is non-transferable. Sub-licensing is prohibited.

TERRITORY. The license applies globally, limited to Synergy’s internal business operations across its offices in North America, Europe, and Asia.

SERVICES. Quantum will provide Standard Support (8x5, Pacific Time) and basic implementation services as outlined in Exhibit A. Standard Support includes 24-hour response time for non-critical issues and 4-hour response time for critical incidents, as per SLA in Exhibit B.

DELIVERABLES. Key deliverables include the configured FusionPlatform instance, access credentials, integration documentation, and onboarding training sessions for Synergy's admin team.

FEES. Synergy shall pay Quantum a total Subscription Fee of $150,000 USD annually, due Net 30 days from the start of each subscription year. Implementation Services fee is a one-time charge of $25,000 USD due upon signing. Payment milestones:
- Year 1 subscription: $150,000 – due July 15, 2024
- Implementation: $25,000 – due July 10, 2024
- Subsequent subscriptions: $150,000 annually on July 15, 2025 and July 15, 2026

PENALTIES. Late payments accrue 1.5% monthly interest. Breach of SLA response time commitments will result in service credits of up to 5% of monthly subscription fee.

TERM AND TERMINATION. This Agreement commences on the Effective Date and continues for three (3) years. It renews automatically for successive 1-year terms unless either party provides written notice of non-renewal at least 90 days prior to the end of the then-current term. Either party may terminate for material breach upon 30 days' written notice if the breach remains uncured.

CONFIDENTIALITY. Each party agrees to maintain confidentiality of all proprietary information exchanged under this Agreement. Obligations last for 5 years post-termination.

DATA PRIVACY. Both parties shall comply with all applicable data privacy laws including the CCPA and GDPR. Quantum agrees not to access, share, or store any client data unless explicitly authorized.

IP OWNERSHIP. All intellectual property rights in FusionPlatform, including its components and updates, remain solely with Quantum. Synergy shall not reverse engineer, decompile, or copy the software.

INSURANCE. Quantum shall maintain professional liability and cyber insurance coverage of at least $2 million throughout the term of this Agreement.

GOVERNING LAW & JURISDICTION. This Agreement is governed by the laws of the State of California, without regard to conflict of law principles. Disputes shall be resolved exclusively in the state or federal courts located in Santa Clara County, California.

ACCEPTANCE. Use of the software constitutes acceptance. Delivery shall occur within 5 business days of Effective Date.

IN WITNESS WHEREOF... [Signatures]

Exhibit A: Services Description (Attached)  
Exhibit B: SLA & Support Commitments  
Amendment No. 1: Pricing Adjustment (Dated Aug 1, 2024 - Attached)
"""


# --- Contract Analysis Function ----
def extract_contract_data_from_text(contract_text: str) -> Optional[ContractAnalysisResult]:
    if not contract_text:
        logging.error("Contract text is empty.")
        return None

    logging.info("Running contract analysis using pydantic-ai Agent...")

    try:
        result = agent.run_sync(contract_text)
        logging.info("Extraction successful.")
        return result.data  # result is usually an `AgentResult` wrapper

    except ValidationError as e:
        logging.error("Validation failed.")
        logging.error(f"Validation Errors: {e.errors()}")
        return None

    except Exception as e:
        logging.error(f"Unexpected error during extraction: {type(e).__name__} - {e}")
        return None


# --- Run it ---
if __name__ == "__main__":
    GEMINI_MODEL = "gemini-1.5-flash-latest"
    agent = None
    try:
        agent = Agent(
            model=GEMINI_MODEL,
            result_type=ContractAnalysisResult
        )
        output = extract_contract_data_from_text(contract_text)
        if output:
            print(output.model_dump_json(indent=2))
        else:
            print("Failed to extract contract info.")
    
    except RecursionError as e: # Catch RecursionError specifically
        logging.error(f"!!! RecursionError occurred : {e}")
        import traceback
        logging.error(traceback.format_exc())
        print("\n--- Extraction Failed (Recursion Error with 3 Complex Fields) ---")
    except Exception as e:
        logging.error(f"Unexpected error during Agent execution: {type(e).__name__}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        print("\n--- Extraction Failed (Unexpected Error) ---")
    