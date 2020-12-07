class WebsiteEntry:

    def __init__(self, date, time, ip_src, ip_dst, method, website, path):
        self.date = date
        self.time = time
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.method = method
        self.website = website
        self.path = path
