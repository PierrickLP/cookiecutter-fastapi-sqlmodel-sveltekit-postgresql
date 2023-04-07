import {
	PUBLIC_APP_ENV,
	PUBLIC_APP_DOMAIN_DEV,
	PUBLIC_APP_DOMAIN_STAG,
	PUBLIC_APP_DOMAIN_PROD,
	PUBLIC_APP_NAME
} from '$env/static/public';

let envApiUrl = '';

if (PUBLIC_APP_ENV === 'production') {
	envApiUrl = `https://${PUBLIC_APP_DOMAIN_PROD}`;
} else if (PUBLIC_APP_ENV === 'staging') {
	envApiUrl = `https://${PUBLIC_APP_DOMAIN_STAG}`;
} else {
	envApiUrl = `http://${PUBLIC_APP_DOMAIN_DEV}`;
}

export const apiUrl = envApiUrl;
export const appName = PUBLIC_APP_NAME;
