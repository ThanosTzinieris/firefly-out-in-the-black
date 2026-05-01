import pygame
from Blasts import Blast
from Game_Objects import Game_Object


class Firefly(Game_Object):
    def __init__(self, settings, screen, image_path, alt_image_path):
        super().__init__(settings, screen, 0.50, 0.92, image_path, alt_image_path)
        # Entry state initialization
        self.state = "entering"

        # Skip cinematic entry if already done once
        if settings.serenity_entry_done:
            self.state = "active"

        # Spawn position in logical space
        self.rect.centerx = int(self.settings.logical_width * self.rel_pos_x)
        self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)

        # If entering, spawn below screen
        if self.state == "entering":
            self.target_y = self.rect.centery
            self.rel_pos_y = 1.15  # below visible area
            self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)
        else:
            self.target_y = self.rect.centery

        # Wingspan + canons
        self.canon_offset = int(self.rect.width * 0.08)
        self.wingspan_offset = self.rect.width // 2

        # Movement state
        self.moving_right = False
        self.moving_left = False

        # Shooting state
        self.firing = False

        # Canon cooldown trigger
        self.previous_blast_time = 0


    def fire(self):
        #Returns two plasma blasts on cooldown
        current_time = pygame.time.get_ticks()

        if current_time - self.previous_blast_time >= 400:  # 400ms cooldown
            self.previous_blast_time = current_time  # Update last shot time

            # Wingspan + canons
            self.canon_offset = int(self.rect.width * 0.092)    # Minor fix
            self.wingspan_offset = self.rect.width // 2         # Wingspan adjusts to current size

            left_canon = (self.rect.centerx - self.wingspan_offset + self.canon_offset, self.rect.centery)
            right_canon = (self.rect.centerx + self.wingspan_offset - self.canon_offset, self.rect.centery)

            # Create actual blast instances
            left_blast = Blast(self.settings, self.screen, self.settings.PLASMA_BLAST, "Serenity", left_canon[0], left_canon[1])
            right_blast = Blast(self.settings, self.screen, self.settings.PLASMA_BLAST, "Serenity", right_canon[0], right_canon[1])

            # Enable movement for both blasts
            left_blast.moving = True
            right_blast.moving = True

            return left_blast, right_blast

        return None, None


    def update(self):
        # Entry Phase (animation)
        if self.state == "entering":
            entry_speed = self.settings.logical_height * 0.002

            self.rel_pos_y -= entry_speed / self.settings.logical_height
            self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)

            if self.rect.centery <= self.target_y:
                self.rect.centery = self.target_y
                self.rel_pos_y = self.target_y / self.settings.logical_height
                self.state = "active"
                self.settings.serenity_entry_done = True

            return

        # Logical movement speed (independent of screen size)
        self.speed_factor = self.settings.logical_width * 0.005
        
        # Logical movement boundaries
        if self.moving_right and self.rect.right < self.settings.logical_width:
            gap = self.settings.logical_width - self.rect.right
            self.rect.centerx += min(self.speed_factor, gap)
            self.rel_pos_x = self.rect.centerx / self.settings.logical_width

        if self.moving_left and self.rect.left > 0:
            gap = self.rect.left    # minus zero
            self.rect.centerx -= min(self.speed_factor, gap)
            self.rel_pos_x = self.rect.centerx / self.settings.logical_width


    def explode(self):
        if not self.alt_active:
            center = self.rect.center
            self.active_image = self.alt_scaled
            self.rect = self.active_image.get_rect(center=center)
            self.alt_active = True