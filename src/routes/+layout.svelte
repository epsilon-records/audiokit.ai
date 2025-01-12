<script lang="ts">
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
	import '../app.css';
	import Nav from '$lib/components/ui/Nav.svelte';
	let { children } = $props();

	const queryClient = new QueryClient();
</script>

<QueryClientProvider client={queryClient}>
	<Nav />
	{@render children()}
</QueryClientProvider>