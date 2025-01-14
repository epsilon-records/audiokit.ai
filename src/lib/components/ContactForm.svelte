<script lang="ts">
  import { Button } from '$lib/components/ui/button';
</script>

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
