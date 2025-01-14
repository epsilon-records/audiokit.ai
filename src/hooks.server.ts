import type { Handle } from '@sveltejs/kit'
import { sequence } from '@sveltejs/kit/hooks'
import { handleClerk } from 'clerk-sveltekit/server'
import { CLERK_SECRET_KEY } from '$env/static/private'
import { pb } from '$lib/pocketbase'
import { serializeNonPOJOs } from '$lib/utils'

export const handle: Handle = sequence(
	async ({ event, resolve }) => {
 		event.locals.pb = pb
		event.locals.pb.authStore.loadFromCookie(event.request.headers.get('cookie') || '')

		if (event.locals.pb.authStore.isValid) {
			event.locals.user = serializeNonPOJOs(event.locals.pb.authStore.model)
		} else {
			event.locals.user = undefined
		}
		const response = await resolve(event)
		response.headers.set('set-cookie', event.locals.pb.authStore.exportToCookie())
		return response
	},
	handleClerk(CLERK_SECRET_KEY, {
		debug: true,
		protectedPaths: ['/admin'],
		signInUrl: '/sign-in',
	})
)