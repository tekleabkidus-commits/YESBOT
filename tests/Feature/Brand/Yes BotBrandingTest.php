<?php

declare(strict_types=1);

use App\Models\MenuItem;
use App\Services\SettingsService;
use Database\Seeders\MenuSeeder;
use Database\Seeders\SettingsSeeder;

it('uses the Yes Bot name and never seeds links to another operator', function () {
    $this->seed(SettingsSeeder::class);
    $this->seed(MenuSeeder::class);

    $settings = app(SettingsService::class);
    $welcome = (array) $settings->get('welcome.message');

    expect($welcome['en'])->toContain('Yes Bot')
        ->and($settings->get('webapp.url'))->toBeNull()
        ->and(MenuItem::query()->whereNotNull('url')->count())->toBe(0)
        ->and(MenuItem::query()->whereHas('translations', fn ($q) => $q->where('label', 'ℹ️ About Yes Bot'))->exists())->toBeTrue();
});

it('ships the distinct violet Yes Bot theme', function () {
    expect(file_exists(public_path('css/yesbot-theme.css')))->toBeTrue()
        ->and(file_get_contents(public_path('css/yesbot-theme.css')))->toContain('#6d28d9')
        ->and(file_exists(public_path('yesbot-alt-mark.svg')))->toBeTrue();
});
