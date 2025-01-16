<script lang="ts">
  import { Button } from '$lib/components/ui/button';
</script>

<div class="flex flex-col gap-6">
  <p class="text-lg text-cyan-900">
    Get in touch with Epsilon Records for demos, bookings, or general inquiries.
  </p>

  <form class="flex flex-col gap-6">
    <div>
      <label for="name" class="text-sm text-cyan-900 uppercase mb-1 block">Name</label>
      <input
        type="text"
        id="name"
        name="name"
        required
        class="w-full bg-cyan-100 border border-cyan-900 p-2 text--cyan-900 focus:outline-none focus:border-[#ff00ff] transition-colors"
      />
    </div>

    <div>
      <label for="email" class="text-sm text-cyan-900 uppercase mb-1 block">Email</label>
      <input
        type="email"
        id="email"
        name="email"
        required
        class="w-full bg-cyan-100 border border-cyan-900 p-2 text-cyan-900 focus:outline-none focus:border-[#ff00ff] transition-colors"
      />
    </div>

    <div>
      <label for="subject" class="text-sm text--cyan-900 uppercase mb-1 block">Subject</label>
      <select
        id="subject"
        name="subject"
        required
        class="w-full bg-cyan-100 border border-cyan-900 p-2 text-cyan-900 focus:outline-none focus:border-[#ff00ff] transition-colors"
      >
        <option value="demo">Demo Submission</option>
        <option value="booking">Booking Request</option>
        <option value="press">Press Inquiry</option>
        <option value="other">Other</option>
      </select>
    </div>

    <div>
      <label for="message" class="text-sm text-cyan-900 uppercase mb-1 block">Message</label>
      <textarea
        id="message"
        name="message"
        required
        rows="6"
        class="w-full bg-cyan-100 border border-cyan-900 p-2 text-cyan-900 focus:outline-none focus:border-[#ff00ff] transition-colors resize-none"
      ></textarea>
    </div>

    <Button
      type="submit"
      variant="outline"
      class="bg-cyan-300 border-cyan-900 text-black hover:bg-cyan-900 hover:text-white w-full md:w-auto"
    >
      Send Message
    </Button>
  </form>
</div>
