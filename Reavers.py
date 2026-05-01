import pygame
import random
from Blasts import Blast
from Game_Objects import Game_Object


class Reaver(Game_Object):
    def __init__(self, settings, screen, rel_pos_x, rel_pos_y, image_path, alt_image_path):
        super().__init__(settings, screen, rel_pos_x, rel_pos_y, image_path, alt_image_path)

        # Spawn position in logical space (same pattern as Firefly)
        self.rect.centerx = int(self.settings.logical_width  * rel_pos_x)
        self.rect.centery = int(self.settings.logical_height * rel_pos_y)

        # Canon cooldown trigger
        self.previous_blast_time = 0  # Tracks the last time the Reaver ship fired

        # Prime entry animation
        self.state = "entering"

        # Set life state
        #self.alive = True

        # Prime death animation
        self.remove_after_frames = 0

        # Store target position
        self.target_y = self.rect.centery

        # Determine entry spawn Y (relative)
        if rel_pos_y > 0.15:  # Row 2
            spawn_rel_y = -0.10
        else:  # Row 1
            spawn_rel_y = -0.25

        # Override starting position
        self.rel_pos_y = spawn_rel_y
        self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)


    def update(self):

        # -----------------------------------------------------------
        # Entry Phase
        # -----------------------------------------------------------
        if self.state == "entering":
            self.speed_factor = self.settings.logical_height * 0.002

            self.rel_pos_y += self.speed_factor / self.settings.logical_height
            self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)

            if self.rect.centery >= self.target_y:
                self.rect.centery = self.target_y
                self.rel_pos_y = self.target_y / self.settings.logical_height
                self.state = "active"

            return None


        # -----------------------------------------------------------
        # Dying Phase
        # -----------------------------------------------------------
         
        # Start countdown for final frames
        if self.remove_after_frames > 0:
            self.remove_after_frames -= 1
            if self.remove_after_frames == 0:
                return False
            return None


        # -----------------------------------------------------------
        # Active Phase
        # -----------------------------------------------------------

        if self.state != "active":
            return None

        # Randomly returns one harpoon on cooldown
        current_time = pygame.time.get_ticks()

        if current_time - self.previous_blast_time >= 10:  # 10ms cooldown
            self.previous_blast_time = current_time  # Update last shot time

            if random.random() > 0.01:  # 1% chance to actually fire
                return None

            # Canon position
            canon = (self.rect.centerx, self.rect.centery)

            # Create actual blast instances
            harpoon = Blast(self.settings, self.screen, self.settings.HARPOON, "Reaver", canon[0], canon[1])

            # Enable movement for harpoon
            harpoon.moving = True

            return harpoon

        return None


    def explode(self):
        if not self.alt_active:
            center = self.rect.center
            self.active_image = self.alt_scaled
            self.rect = self.active_image.get_rect(center=center)
            self.alt_active = True