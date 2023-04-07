<script>
	import { apiUrl } from '../env';

	let isok = 'NOT OK';
	async function ping() {
		const response = await fetch(apiUrl + '/api/v1/utils/ping/', {
			method: 'GET'
		});

		isok = await response.json();
	}
</script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>

<button on:click={ping}>Ping</button>
{isok}
