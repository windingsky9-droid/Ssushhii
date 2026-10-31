// Owner-editable site settings. No secrets belong here: this file is public.
//
// supportLinks: payment or donation pages that you own and that pay out to
// you (Ko-fi, Buy Me a Coffee, GitHub Sponsors, a Stripe Payment Link, a
// Fiverr gig). The "Support the studio" section and its nav link stay hidden
// until at least one https:// link is listed here.
//
// Example:
//   { label: 'Buy me a coffee', url: 'https://ko-fi.com/your-name', note: 'One-off tip' },
//   { label: 'Commission a scene', url: 'https://buy.stripe.com/your-link', note: 'Custom 3D build' },
//
// shopItems: digital products you sell on a store page you own (Gumroad,
// itch.io, Ko-fi Shop, Lemon Squeezy or a Stripe Payment Link). Paste each
// product's https:// checkout link into its url. The "Shop" section and its
// nav link stay hidden until at least one item has an https:// url, and an
// item without one is never shown. image is a path inside this folder.
window.SITE_CONFIG = {
  supportLinks: [],
  shopItems: [
    { title: 'Celestial Observatory Wallpaper Pack', price: '$5', url: '', image: 'media/shop-wallpapers.jpg', note: 'Eight scenes from the observatory, each as a 4K desktop wallpaper and a phone wallpaper. 16 files.' },
    { title: 'Zodiac Constellations: 12 Star Map Prints', price: '$12', url: '', image: 'media/shop-zodiac-prints.jpg', note: 'All twelve signs drawn from real star positions, in Midnight and Ivory, at 3600×4800 for 12×16 in prints. 24 files.' },
  ],
};
