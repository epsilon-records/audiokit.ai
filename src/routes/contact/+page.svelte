<script lang="ts">
    import { Button } from '$lib/components/ui/button';
</script>

<div class="min-h-screen bg-black text-[#00ff00]">
    <div class="container mx-auto px-4 pt-32 pb-12">
        <h1 class="text-4xl font-bold text-[#00ff00] mb-12">Contact</h1>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div class="flex flex-col gap-6">
                <p class="text-lg text-[#00ffff]">
                    Get in touch with Epsilon Records for demos, bookings, or general inquiries.
                </p>

                <form class="flex flex-col gap-6">
                    <div>
                        <label for="name" class="text-sm text-[#00ffff] uppercase mb-1 block">Name</label>
                        <input 
                            type="text" 
                            id="name" 
                            name="name" 
                            required
                            class="w-full bg-transparent border border-[#00ff00] p-2 text-[#00ff00] focus:outline-none focus:border-[#ff00ff] transition-colors"
                        />
                    </div>

                    <div>
                        <label for="email" class="text-sm text-[#00ffff] uppercase mb-1 block">Email</label>
                        <input 
                            type="email" 
                            id="email" 
                            name="email" 
                            required
                            class="w-full bg-transparent border border-[#00ff00] p-2 text-[#00ff00] focus:outline-none focus:border-[#ff00ff] transition-colors"
                        />
                    </div>

                    <div>
                        <label for="subject" class="text-sm text-[#00ffff] uppercase mb-1 block">Subject</label>
                        <select 
                            id="subject" 
                            name="subject" 
                            required
                            class="w-full bg-black border border-[#00ff00] p-2 text-[#00ff00] focus:outline-none focus:border-[#ff00ff] transition-colors"
                        >
                            <option value="demo">Demo Submission</option>
                            <option value="booking">Booking Request</option>
                            <option value="press">Press Inquiry</option>
                            <option value="other">Other</option>
                        </select>
                    </div>

                    <div>
                        <label for="message" class="text-sm text-[#00ffff] uppercase mb-1 block">Message</label>
                        <textarea 
                            id="message" 
                            name="message" 
                            required
                            rows="6"
                            class="w-full bg-transparent border border-[#00ff00] p-2 text-[#00ff00] focus:outline-none focus:border-[#ff00ff] transition-colors resize-none"
                        ></textarea>
                    </div>

                    <Button 
                        type="submit"
                        variant="outline" 
                        class="border-[#00ff00] text-[#00ff00] hover:bg-[#00ff00] hover:text-black w-full md:w-auto"
                    >
                        Send Message
                    </Button>
                </form>
            </div>

            <div class="flex flex-col gap-6">
                <div>
                    <h2 class="text-sm text-[#00ffff] uppercase mb-1">Address</h2>
                    <p class="text-lg text-[#00ff00]">
                        123 Underground Street<br />
                        Techno District<br />
                        Berlin, 10997<br />
                        Germany
                    </p>
                </div>

                <div>
                    <h2 class="text-sm text-[#00ffff] uppercase mb-1">Email</h2>
                    <a 
                        href="mailto:info@epsilonrecords.com" 
                        class="text-lg text-[#00ff00] hover:text-[#ff00ff] transition-colors"
                    >
                        info@epsilonrecords.com
                    </a>
                </div>

                <div>
                    <h2 class="text-sm text-[#00ffff] uppercase mb-1">Business Hours</h2>
                    <p class="text-lg text-[#00ff00]">
                        Monday - Friday<br />
                        10:00 - 18:00 CET
                    </p>
                </div>
            </div>
        </div>
    </div>
</div> 