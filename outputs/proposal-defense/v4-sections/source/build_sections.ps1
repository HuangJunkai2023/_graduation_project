param(
 [string]$Root='D:/_graduation_project',
 [string]$OutputDir=(Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$source=[IO.Path]::GetFullPath("$Root/outputs/proposal-defense/v3-template/OCS_Proposal_Defense_EN_v3_SWJTU_Template_Bilingual_Notes.pptx")
$template=[IO.Path]::GetFullPath("$Root/docs/交大ppt模板-1.pptx")
$out=[IO.Path]::GetFullPath($OutputDir)
$spec=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sections_content.json') -Raw -Encoding UTF8|ConvertFrom-Json
$blue=0x8C4B19;$dark=0x333333;$white=0xFFFFFF
function SetText($shape,[string]$value,[single]$size,[int]$color,[bool]$bold=$false){
 $shape.TextFrame.TextRange.Text=$value
 $shape.TextFrame.AutoSize=0;$shape.TextFrame.WordWrap=-1
 $shape.TextFrame.MarginLeft=0;$shape.TextFrame.MarginRight=0
 $shape.TextFrame.MarginTop=0;$shape.TextFrame.MarginBottom=0
 $shape.TextFrame.VerticalAnchor=1
 $r=$shape.TextFrame.TextRange
 $r.Font.Name='Arial';$r.Font.Size=$size;$r.Font.Bold=[int]$bold*-1;$r.Font.Color.RGB=$color
 $r.ParagraphFormat.Bullet.Visible=0;$r.ParagraphFormat.Alignment=1
 $r.ParagraphFormat.SpaceBefore=0;$r.ParagraphFormat.SpaceAfter=0
 $r.ParagraphFormat.LineRuleWithin=-1;$r.ParagraphFormat.SpaceWithin=1
 $shape.TextFrame2.TextRange.Font.Fill.Solid()
 $shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB=$color
 $shape.TextFrame2.TextRange.Font.Fill.Transparency=0
}
$pp=$null;$pres=$null;$issues=@();$objects=@();$tableCells=0
function InspectText($shape,$page,$label=''){
 if($shape.HasTextFrame -and $shape.TextFrame.HasText){
  $b=$shape.TextFrame2.TextRange
  if($b.BoundWidth -gt ($shape.Width-$shape.TextFrame.MarginLeft-$shape.TextFrame.MarginRight+2) -or $b.BoundHeight -gt ($shape.Height-$shape.TextFrame.MarginTop-$shape.TextFrame.MarginBottom+2)){
   $script:issues+=@{page=$page;shape=$shape.Name;label=$label;text=$shape.TextFrame.TextRange.Text;width=$shape.Width;height=$shape.Height;boundWidth=$b.BoundWidth;boundHeight=$b.BoundHeight}
  }
 }
}
try{
 $pp=New-Object -ComObject PowerPoint.Application
 $pres=$pp.Presentations.Add(0)
 $pres.PageSetup.SlideWidth=960;$pres.PageSetup.SlideHeight=540
 foreach($row in $spec.slides){
  $i=[int]$row.page
  if($row.kind -eq 'old'){$file=$source;$ref=[int]$row.oldPage}
  else{$file=$template;$ref=[int]$row.template}
  $null=$pres.Slides.InsertFromFile($file,$pres.Slides.Count,$ref,$ref)
  $s=$pres.Slides.Item($i)
  if($row.kind -eq 'contents'){
   $h=$s.Shapes.Item('标题 9');SetText $h 'Contents' 36 $white $true
   $h.Left=98;$h.Top=12;$h.Width=550;$h.Height=52
   $h=$s.Shapes.Item('文本框 142');SetText $h 'PRESENTATION OUTLINE' 18 $white
   $h.Left=98;$h.Top=66;$h.Width=500;$h.Height=25
   $names=@('矩形 149','矩形 223','矩形 224','矩形 225')
   for($j=0;$j -lt 4;$j++){
    $entry=$s.Shapes.Item($names[$j]);SetText $entry ($spec.parts[$j].number+'  '+$spec.parts[$j].title) 26 $dark
    $entry.Left=80;$entry.Top=164+$j*68;$entry.Width=680;$entry.Height=43
   }
   # The original tightly spaced motto overlaps its tiny footer emblem after
   # PowerPoint font substitution. Keep the large native watermark and header.
   for($j=$s.Shapes.Count;$j -ge 1;$j--){
    $shape=$s.Shapes.Item($j)
    if($shape.HasTextFrame -and $shape.TextFrame.HasText -and $shape.TextFrame.TextRange.Text.Contains('竢实扬华')){$shape.Delete()}
    elseif($shape.Type -eq 13 -and $shape.Top -gt 480 -and $shape.Width -lt 50){$shape.Delete()}
   }
  }elseif($row.kind -eq 'part'){
   $p=$row.part
   $h=$s.Shapes.Item('标题 9');SetText $h 'PART' 38 $white $true
   $h.Left=130;$h.Top=25;$h.Width=210;$h.Height=47
   $num=$s.Shapes.Item('文本框 14');SetText $num $p.number 124 $white $true
   $num.Left=113;$num.Top=85;$num.Width=245;$num.Height=160
   $h=$s.Shapes.Item('标题 207');SetText $h $p.breakTitle 32 $blue $true
   $h.Left=420;$h.Top=65;$h.Width=470;$h.Height=92
   $bodyName='文本框 25'
   if($ref -eq 4){$bodyName='文本框 15'}
   if($ref -eq 5){$bodyName='文本框 24'}
   $b=$s.Shapes.Item($bodyName);SetText $b $p.items 21 $dark
   $b.Left=430;$b.Top=155;$b.Width=435;$b.Height=100
  }
  # Refresh all main-slide counters and copied backup references.
  foreach($shape in $s.Shapes){
   if($shape.HasTextFrame -and $shape.TextFrame.HasText){
    $text=$shape.TextFrame.TextRange.Text
    if($row.kind -eq 'old' -and $i -le 18 -and $text -match '^\d{2} / 13$'){
     $shape.TextFrame.TextRange.Text=('{0:00} / 18' -f $i)
    }
   }
  }
  foreach($n in $s.NotesPage.Shapes){
   if($n.Type -eq 14 -and $n.PlaceholderFormat.Type -eq 2){
    $n.TextFrame.TextRange.Text=$row.notes
    $n.TextFrame.TextRange.Font.Name='Microsoft YaHei';$n.TextFrame.TextRange.Font.Size=12
   }
  }
 }
 # Native PowerPoint sections make the four Parts visible in Slide Sorter.
 $null=$pres.SectionProperties.AddBeforeSlide(1,'Opening and Contents')
 foreach($p in $spec.parts){$null=$pres.SectionProperties.AddBeforeSlide([int]$p.start,('Part '+$p.number+' - '+$p.title))}
 $null=$pres.SectionProperties.AddBeforeSlide(19,'Backup Slides')
 foreach($s in $pres.Slides){
  foreach($shape in $s.Shapes){
   InspectText $shape $s.SlideIndex
   if($shape.HasTable){for($r=1;$r -le $shape.Table.Rows.Count;$r++){for($c=1;$c -le $shape.Table.Columns.Count;$c++){InspectText $shape.Table.Cell($r,$c).Shape $s.SlideIndex "cell $r,$c";$tableCells++}}}
   $objects+=@{page=$s.SlideIndex;name=$shape.Name;type=$shape.Type;x=$shape.Left;y=$shape.Top;width=$shape.Width;height=$shape.Height;text=$(if($shape.HasTextFrame){$shape.TextFrame.TextRange.Text}else{''})}
  }
 }
 $pptx=Join-Path $out 'OCS_Proposal_Defense_EN_v4_SWJTU_Sections.pptx'
 $pdf=Join-Path $out 'OCS_Proposal_Defense_EN_v4_SWJTU_Sections.pdf'
 $pres.SaveAs($pptx,24)
 $pres.SaveAs($pdf,32)
 foreach($s in $pres.Slides){$s.Export((Join-Path $out ('previews/slide-{0:00}.png' -f $s.SlideIndex)),'PNG',1600,900)}
 @{slides=$pres.Slides.Count;mainSlides=18;backupSlides=5;sectionCount=$pres.SectionProperties.Count;overflowCount=$issues.Count;overflows=$issues;tableCellsInspected=$tableCells}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $out 'validation/powerpoint-layout.json') -Encoding UTF8
 $objects|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $out 'validation/powerpoint-objects.json') -Encoding UTF8
 Write-Output ('Slides: '+$pres.Slides.Count+'; sections: '+$pres.SectionProperties.Count+'; text overflow flags: '+$issues.Count)
 Write-Output $pptx
}finally{
 if($pres){$pres.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($pres)|Out-Null}
 if($pp){[Runtime.InteropServices.Marshal]::ReleaseComObject($pp)|Out-Null}
}
