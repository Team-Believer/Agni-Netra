import { EventItem, EventDetail } from './types';

export interface VerificationContactResult {
  name: string;
  role: string;
  phone: string;
  formattedPhone: string;
  contactType: 'Facility' | 'Forest Authority' | 'District Authority' | 'Municipal Authority' | 'Local Authority';
  source: string;
  actionLabel: string;
  isVerifiedPublic: boolean;
}

/**
 * Contextually resolves verified official organizational contact information based on the current event.
 * Uses official facility control rooms, district disaster management cells, or forest authorities.
 * No personal or private numbers are exposed.
 */
export function resolveVerificationContact(
  event: EventItem | EventDetail | null | undefined
): VerificationContactResult | null {
  if (!event) return null;

  const facility = (event.nearby_facility || '').toLowerCase();
  const title = (event.title || '').toLowerCase();
  const classification = (event.classification || '').toLowerCase();
  const location = (event.location || '').toLowerCase();
  const district = (event.district || '').toLowerCase();
  const state = (event.state || '').toLowerCase();
  const eventId = (event.event_id || '').toUpperCase();

  // 1. Digboi Refinery (EVENT-SEED-008 / Digboi / Assam)
  if (
    eventId === 'EVENT-SEED-008' ||
    facility.includes('digboi') ||
    location.includes('digboi') ||
    title.includes('digboi')
  ) {
    return {
      name: 'IndianOil Digboi Refinery Control Desk',
      role: 'Official Facility Control Room',
      phone: '03751262000',
      formattedPhone: '03751-262000',
      contactType: 'Facility',
      source: 'IndianOil Official Public Directory',
      actionLabel: 'Call Facility Desk',
      isVerifiedPublic: true,
    };
  }

  // 2. Jamnagar Refinery (EVENT-SEED-005 / Jamnagar / Reliance)
  // Per requirement: Jamnagar district emergency control room (0288-2553404 / 0288-1077)
  if (
    eventId === 'EVENT-SEED-005' ||
    facility.includes('reliance') ||
    location.includes('jamnagar') ||
    district.includes('jamnagar') ||
    title.includes('jamnagar')
  ) {
    return {
      name: 'District Disaster & Emergency Control Room (Jamnagar)',
      role: 'District Disaster Management Cell',
      phone: '02882553404',
      formattedPhone: '0288-2553404',
      contactType: 'District Authority',
      source: 'Jamnagar District Emergency Portal',
      actionLabel: 'Contact District Authority',
      isVerifiedPublic: true,
    };
  }

  // 3. Simlipal National Park (EVENT-SEED-009 / Simlipal / Mayurbhanj Forest Fire)
  if (
    eventId === 'EVENT-SEED-009' ||
    facility.includes('simlipal') ||
    location.includes('simlipal') ||
    (district.includes('mayurbhanj') && classification.includes('forest'))
  ) {
    return {
      name: 'Simlipal Forest Division / Odisha Fire Control Room',
      role: 'Official Forest & Fire Authority',
      phone: '06792252570',
      formattedPhone: '06792-252570',
      contactType: 'Forest Authority',
      source: 'Odisha Forest Dept / Simlipal Biosphere Directory',
      actionLabel: 'Contact Forest Authority',
      isVerifiedPublic: true,
    };
  }

  // 4. Korba Super Thermal Power (EVENT-SEED-002 / Korba)
  if (
    eventId === 'EVENT-SEED-002' ||
    facility.includes('korba') ||
    location.includes('korba') ||
    district.includes('korba')
  ) {
    return {
      name: 'Korba Super Thermal Power Station Control Room',
      role: 'Official Plant Operations Desk',
      phone: '07759224120',
      formattedPhone: '07759-224120',
      contactType: 'Facility',
      source: 'NTPC Korba Industrial Public Directory',
      actionLabel: 'Call Facility Desk',
      isVerifiedPublic: true,
    };
  }

  // 5. Bokaro Steel Plant (EVENT-SEED-006 / Bokaro)
  if (
    eventId === 'EVENT-SEED-006' ||
    facility.includes('bokaro') ||
    location.includes('bokaro') ||
    district.includes('bokaro')
  ) {
    return {
      name: 'Bokaro Steel Plant Industrial Safety Control Desk',
      role: 'Official Plant Safety Office',
      phone: '06542240333',
      formattedPhone: '06542-240333',
      contactType: 'Facility',
      source: 'SAIL Bokaro Industrial Safety Directory',
      actionLabel: 'Call Plant Desk',
      isVerifiedPublic: true,
    };
  }

  // 6. Barnawapara Reserve (EVENT-SEED-003 / Barnawapara / Raipur Forest)
  if (
    eventId === 'EVENT-SEED-003' ||
    facility.includes('barnawapara') ||
    location.includes('barnawapara')
  ) {
    return {
      name: 'Raipur Forest Division & Sanctuary Range Desk',
      role: 'Official Forest Range Control',
      phone: '07712423982',
      formattedPhone: '0771-2423982',
      contactType: 'Forest Authority',
      source: 'Chhattisgarh Forest Dept Public Directory',
      actionLabel: 'Contact Forest Authority',
      isVerifiedPublic: true,
    };
  }

  // 7. Paradip Port Industries (EVENT-SEED-010 / Paradip)
  if (
    eventId === 'EVENT-SEED-010' ||
    facility.includes('paradip') ||
    location.includes('paradip')
  ) {
    return {
      name: 'Paradip Port Safety & Chemical Terminal Desk',
      role: 'Official Port Safety Control',
      phone: '06722222158',
      formattedPhone: '06722-222158',
      contactType: 'Facility',
      source: 'Paradip Port Authority Public Directory',
      actionLabel: 'Call Port Desk',
      isVerifiedPublic: true,
    };
  }

  // 8. Ghazipur Landfill Facility (EVENT-SEED-012 / Ghazipur)
  if (
    eventId === 'EVENT-SEED-012' ||
    facility.includes('ghazipur') ||
    location.includes('ghazipur')
  ) {
    return {
      name: 'East Delhi Municipal Corporation & Fire Control',
      role: 'Municipal Solid Waste Control Desk',
      phone: '01122780000',
      formattedPhone: '011-22780000',
      contactType: 'Municipal Authority',
      source: 'MCD Public Control Room Directory',
      actionLabel: 'Contact Municipal Authority',
      isVerifiedPublic: true,
    };
  }

  // 9. Bhilai Steel Plant (EVENT-SEED-001 / Bhilai / Durg)
  if (
    eventId === 'EVENT-SEED-001' ||
    facility.includes('bhilai') ||
    location.includes('bhilai') ||
    district.includes('durg')
  ) {
    return {
      name: 'Bhilai Steel Plant Operations & Safety Desk',
      role: 'Official Plant Control Desk',
      phone: '07882223001',
      formattedPhone: '0788-2223001',
      contactType: 'Facility',
      source: 'SAIL Bhilai Public Directory',
      actionLabel: 'Call Plant Desk',
      isVerifiedPublic: true,
    };
  }

  // 10. Jharia Coalfield (EVENT-SEED-011 / Jharia / Dhanbad)
  if (
    eventId === 'EVENT-SEED-011' ||
    facility.includes('jharia') ||
    location.includes('jharia') ||
    district.includes('dhanbad')
  ) {
    return {
      name: 'BCCL Jharia Coal Mining & Safety Control',
      role: 'Official Mining Safety Desk',
      phone: '03262230100',
      formattedPhone: '0326-2230100',
      contactType: 'Facility',
      source: 'BCCL Dhanbad Mining Directory',
      actionLabel: 'Call Mining Desk',
      isVerifiedPublic: true,
    };
  }

  // 11. Nagpur Industrial Zone (EVENT-SEED-014 / Nagpur)
  if (
    eventId === 'EVENT-SEED-014' ||
    facility.includes('nagpur') ||
    location.includes('nagpur') ||
    district.includes('nagpur')
  ) {
    return {
      name: 'MIDC Hingna Industrial Safety Office',
      role: 'Official Industrial Zone Control',
      phone: '07104237444',
      formattedPhone: '07104-237444',
      contactType: 'District Authority',
      source: 'MIDC Maharashtra Public Directory',
      actionLabel: 'Contact Industrial Office',
      isVerifiedPublic: true,
    };
  }

  // 12. Agricultural Burns (Karnal / Ludhiana / Bemetara)
  if (
    eventId === 'EVENT-SEED-013' ||
    location.includes('karnal') ||
    district.includes('karnal')
  ) {
    return {
      name: 'District Agriculture & Emergency Control Office (Karnal)',
      role: 'Official District Agriculture Cell',
      phone: '01842267101',
      formattedPhone: '0184-2267101',
      contactType: 'District Authority',
      source: 'Karnal District Administration Directory',
      actionLabel: 'Contact District Authority',
      isVerifiedPublic: true,
    };
  }

  if (
    eventId === 'EVENT-SEED-007' ||
    location.includes('ludhiana') ||
    district.includes('ludhiana')
  ) {
    return {
      name: 'District Agriculture & Fire Control Office (Ludhiana)',
      role: 'Official District Authority',
      phone: '01612401960',
      formattedPhone: '0161-2401960',
      contactType: 'District Authority',
      source: 'Ludhiana District Administration Directory',
      actionLabel: 'Contact District Authority',
      isVerifiedPublic: true,
    };
  }

  if (
    eventId === 'EVENT-SEED-004' ||
    location.includes('bemetara') ||
    district.includes('bemetara')
  ) {
    return {
      name: 'District Agriculture & Emergency Control Office (Bemetara)',
      role: 'Official District Authority',
      phone: '07824222100',
      formattedPhone: '07824-222100',
      contactType: 'District Authority',
      source: 'Bemetara District Administration Directory',
      actionLabel: 'Contact District Authority',
      isVerifiedPublic: true,
    };
  }

  // 13. Contextual Fallbacks by Event Classification
  if (
    classification.includes('forest') ||
    title.includes('forest') ||
    facility.includes('reserve') ||
    facility.includes('national park')
  ) {
    const locName = event.district || event.state || 'Local';
    return {
      name: `${locName} Forest Division & Fire Control Desk`,
      role: 'Official Forest Department Contact',
      phone: '1926',
      formattedPhone: '1926 (Toll-Free Forest Helpline)',
      contactType: 'Forest Authority',
      source: 'State Forest Department Helpline',
      actionLabel: 'Contact Forest Authority',
      isVerifiedPublic: true,
    };
  }

  if (
    classification.includes('agricultural') ||
    classification.includes('stubble') ||
    title.includes('crop') ||
    title.includes('farm') ||
    facility.includes('farm') ||
    facility.includes('agricultural')
  ) {
    const locName = event.district || event.state || 'District';
    return {
      name: `${locName} District Agriculture & Fire Control Office`,
      role: 'Official District Agricultural Cell',
      phone: '1077',
      formattedPhone: '1077 (District Disaster Control)',
      contactType: 'District Authority',
      source: 'District Administration Directory',
      actionLabel: 'Contact District Authority',
      isVerifiedPublic: true,
    };
  }

  if (
    classification.includes('industrial') ||
    classification.includes('flare') ||
    classification.includes('refinery') ||
    classification.includes('power') ||
    classification.includes('mining') ||
    classification.includes('steel')
  ) {
    const locName = event.nearby_facility || event.district || event.state || 'Industrial Site';
    return {
      name: `${locName} Control Desk / Safety Office`,
      role: 'Official Industrial Control Desk',
      phone: '1077',
      formattedPhone: '1077 (District Emergency Control)',
      contactType: 'Facility',
      source: 'District Industrial Emergency Register',
      actionLabel: 'Call Facility Desk',
      isVerifiedPublic: true,
    };
  }

  // 14. General / District Control Room Fallback (National Standard District Helpline 1077)
  if (event.district || event.state || event.location) {
    const districtName = event.district || event.state || 'District';
    return {
      name: `${districtName} Disaster Management Control Room`,
      role: 'Official District Control Room',
      phone: '1077',
      formattedPhone: '1077 (District Control Helpline)',
      contactType: 'Local Authority',
      source: 'National Disaster Management Portal (NDMA)',
      actionLabel: 'Contact Local Authority',
      isVerifiedPublic: true,
    };
  }

  // No verified contact available
  return null;
}
