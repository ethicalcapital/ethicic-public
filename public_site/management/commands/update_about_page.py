from django.core.management.base import BaseCommand

from public_site.models import AboutPage


class Command(BaseCommand):
    help = "Update AboutPage content from about_text.md"

    def handle(self, *args, **options):
        # Get the first AboutPage instance (there should only be one)
        try:
            about_page = AboutPage.objects.first()
            if not about_page:
                self.stdout.write(self.style.ERROR("No AboutPage found in database"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error accessing AboutPage: {e}"))
            return

        # Update professional_background_content with "What I do around here" and "What I did Before This"
        professional_content = """
<h3>What I do around here</h3>
<p>I sit in the center of the Ethical Capital Investment Collaborative, and spend most of my time translating insights from our clients, colleagues, and research into our investment strategies.</p>
<p>That means much more than just picking stocks that go up and avoiding ones that go down. Our process is oriented towards cumulative learning, which means I spend most of my time understanding companies, the communities they serve, and the consequences of their activities.</p>
<p>I also get to spend a lot of time getting to know our clients, which I find profoundly grounding.</p>

<h3>What I did Before This</h3>
<p>I've been working in investment management since I graduated from high school.</p>
<p>After spending some time at a regional brokerage firm and a Bangalore-based family office, I joined the staff at the nonprofit CFA Institute while I was still a sophomore in college.</p>
<p>I then spent close to a decade partnering with some of the most interesting investors on the planet to create educational materials aimed at advancing the craft of investment management. In the process, I wrote dozens of articles, edited hundreds, and got to speak to communities of investment professionals all around the world.</p>
<p>I also realized that mainstream firms were only scratching the surface of what's possible in sustainable investment management. That observation would eventually lead me to start this firm.</p>
"""

        # Update external_roles_content with "What I do Besides This"
        external_roles_content = """
<h3>What I do Besides This</h3>
<ul class="external-roles">
<li>Co-host <a href="https://freemoneypodcast.org">Free Money with Sloane and Ashby</a>, a darn good podcast.</li>
<li>Spend as much time as I can justify skiing at one of Utah's many awesome resorts.</li>
<li>Kill my lawn and replace it with perennial wildflowers and other compelling habitats for wildlife.</li>
<li>Serve as a board member at <strong>Responsible Alpha</strong>, a consultancy that supports organizations as they transition towards sustainability.</li>
<li>Support my colleagues at the <strong>Woodcache Public Benefit Corporation</strong>, a carbon removal company I co-founded.</li>
</ul>
"""

        # Update speaking_writing_content with "Things I've Written" and "Book Me As a Speaker"
        speaking_writing_content = """
<h3>Things I've Written</h3>
<p>If you want to understand my personal journey, <a href="/blog/how-i-became-an-active-manager/">this essay on how I became an active manager</a> is the best place to start.</p>
<p>Besides that, here are a few other pieces I've written here:</p>
<ul>
<li><a href="/blog/what-would-a-recession-actually-mean-for-long-term-investors/">What Would a Recession Actually Mean for Long-Term Investors?</a></li>
<li><a href="/blog/what-does-inflation-mean-to-you/">What Does Inflation Mean to You?</a></li>
<li><a href="/blog/what-should-you-expect-when-youre-investing/">What Should You Expect When You're Investing?</a></li>
</ul>
<p>I've also written a textbook on investment idea generation and essays on all sorts of things.</p>
<p>If you want to understand the values that drive my approach to finance, check out <a href="/blog/can-financial-advisers-make-their-clients-happy/">Can Financial Advisers Make Their Clients Happy</a> and <a href="/blog/finance-shouldnt-think-small/">Finance Shouldn't Think Small</a>, which I wrote almost ten years ago.</p>

<h3>Book Me As a Speaker</h3>
<p>I love public speaking! I've given keynote addresses in all sorts of forums and moderated/participated in more panel conversations than I can count.</p>
<p>Whether you're looking for someone to talk to novice investors about aligning their money with their values or a crash course on modern sustainable investing, I'd love to participate.</p>
<p><a href="https://pub-324a685032214395a8bcad478c265d4b.r2.dev/Sloane-Ortel-Speaker-Bio.pdf" class="garden-action secondary">Click here to download my speaker bio</a>, and don't hesitate to reach out directly to talk further.</p>
"""

        # Update the fields
        about_page.professional_background_content = professional_content
        about_page.external_roles_content = external_roles_content
        about_page.speaking_writing_content = speaking_writing_content

        # Save the page
        try:
            about_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Successfully updated AboutPage content"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving AboutPage: {e}"))
