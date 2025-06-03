import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Fetches content from a given URL and writes it to a file."

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="The URL to fetch.")
        parser.add_argument(
            "--output",
            type=str,
            default="output.txt",
            help="Optional output filename (default: output.txt)",
        )

    def handle(self, *args, **options):
        url = options["url"]
        output_file = options["output"]

        job_description_text = self.fetch_job_details(url)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(job_description_text)

        self.stdout.write(
            self.style.SUCCESS(f"Saved response to {output_file}")
        )

    def fetch_job_details(self, url):
        """
        Retrieves the job posting details from a website at the provided URL

        Returns:
            - Text containing job posting information
        """
        description_string = None

        try:
            # Retrieve HTML content from website at URL
            self.stdout.write(f"Fetching: {url}")
            response = requests.get(url)
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            # Retrieve the job posting text from the HTML content
            description_html = soup.find(
                "div", class_="description__text"
            )
            description_string = (
                description_html.get_text(strip=True, separator="\n")
                if description_html
                else ""
            )
        except requests.RequestException as e:
            raise CommandError(f"Request failed: {e}")

        return description_string
