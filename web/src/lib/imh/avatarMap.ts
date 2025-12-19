import type { Investor } from '@/lib/imh/data';

// NOTE:
// - These files live under `web/public/avatars/` and are served as `/avatars/<filename>`.
// - If an id is missing here, UI will fallback to initials avatar.
export const AVATAR_FILENAME_BY_ID: Record<string, string> = {
  warren_buffett: 'warren_buffett.jpg',
  charlie_munger: 'charlie_munger.jpg',
  seth_klarman: 'seth_klarman.jpg',
  ray_dalio: 'ray_dalio.jpg',
  george_soros: 'george_soros.jpg',
  howard_marks: 'howard_marks.jpg',
  carl_icahn: 'carl_icahn.jpg',
  james_simons: 'james_simons.jpg',
  greg_abel: 'greg_abel.jpg',
  // peter_lynch: '',
  // stanley_druckenmiller: '',
  // michael_burry: '',
  // ed_thorp: '',
  // cliff_asness: '',
  // duan_yongping: '',
  // qiu_guolu: '',
  // feng_liu: '',
};

export function getAvatarUrl(investor: Pick<Investor, 'id'>) {
  const filename = AVATAR_FILENAME_BY_ID[investor.id];
  if (!filename) return null;
  // Works in both deployments:
  // - served at / (e.g. rag_service mounts web at "/")
  // - served under /imh (e.g. mounted into another FastAPI app)
  let basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
  if (typeof window !== 'undefined') {
    basePath = window.location.pathname.startsWith('/imh') ? '/imh' : '';
  }
  return `${basePath}/avatars/${filename}`;
}
