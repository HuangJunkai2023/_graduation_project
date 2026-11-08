param(
 [string]$Candidate='D:/_graduation_project/.codex-build/proposal-defense-v2/candidate.pptx',
 [string]$OutputDir='D:/_graduation_project/outputs/proposal-defense/v2'
)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$outputRoot=[System.IO.Path]::GetFullPath($OutputDir)
$candidatePath=[System.IO.Path]::GetFullPath($Candidate)
$pptxPath=Join-Path $outputRoot 'OCS_Proposal_Defense_EN_v2.pptx'
$pdfPath=Join-Path $outputRoot 'OCS_Proposal_Defense_EN_v2.pdf'
$previewDir=Join-Path $outputRoot 'previews'
New-Item -ItemType Directory -Force -Path $previewDir | Out-Null
$pp=$null; $pres=$null; $issues=@(); $inventory=@(); $tableCellChecks=0
function Inspect-Text($shape,[int]$page,[string]$label=''){
 if($shape.HasTextFrame -and $shape.TextFrame.HasText){
   $r=$shape.TextFrame2.TextRange
   $text=$shape.TextFrame.TextRange.Text
   $marginW=$shape.TextFrame.MarginLeft+$shape.TextFrame.MarginRight
   $marginH=$shape.TextFrame.MarginTop+$shape.TextFrame.MarginBottom
   if($r.BoundWidth -gt ($shape.Width-$marginW+2) -or $r.BoundHeight -gt ($shape.Height-$marginH+2)){
     $script:issues+=@{page=$page;shape=$shape.Name;label=$label;width=$shape.Width;height=$shape.Height;boundWidth=$r.BoundWidth;boundHeight=$r.BoundHeight;text=$text}
   }
 }
}
try{
 $pp=New-Object -ComObject PowerPoint.Application
 $pres=$pp.Presentations.Open($candidatePath,0,0,0)
 foreach($slide in $pres.Slides){
   $i=$slide.SlideIndex
   foreach($n in $slide.NotesPage.Shapes){
      if($n.Type -eq 14 -and $n.PlaceholderFormat.Type -eq 2){
        $n.TextFrame.TextRange.Font.Name='Microsoft YaHei'
        $n.TextFrame.TextRange.Font.Size=12
      }
   }
   foreach($shape in $slide.Shapes){
     Inspect-Text $shape $i
     if($shape.HasTable){
       for($r=1;$r -le $shape.Table.Rows.Count;$r++){
         for($c=1;$c -le $shape.Table.Columns.Count;$c++){
           Inspect-Text $shape.Table.Cell($r,$c).Shape $i "cell $r,$c"
           $tableCellChecks++
         }
       }
     }
     $inventory+=@{page=$i;name=$shape.Name;type=$shape.Type;x=$shape.Left;y=$shape.Top;width=$shape.Width;height=$shape.Height;text=$(if($shape.HasTextFrame){$shape.TextFrame.TextRange.Text}else{''})}
   }
 }
 $pres.SaveAs($pptxPath,24)
 $pres.SaveAs($pdfPath,32)
 foreach($slide in $pres.Slides){
   $name='slide-{0:00}.png' -f $slide.SlideIndex
   $slide.Export((Join-Path $previewDir $name),'PNG',1600,900)
 }
 @{slides=$pres.Slides.Count;slideWidth=$pres.PageSetup.SlideWidth;slideHeight=$pres.PageSetup.SlideHeight;overflowCount=$issues.Count;overflows=$issues;tableCellsInspected=$tableCellChecks;method='Native PowerPoint export and TextFrame2 bounds, including table cells';fonts=@('Arial','Microsoft YaHei')}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $outputRoot 'validation/powerpoint-layout.json') -Encoding UTF8
 $inventory|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $outputRoot 'validation/powerpoint-objects.json') -Encoding UTF8
 Write-Output ('Slides: '+$pres.Slides.Count+'; text overflow flags: '+$issues.Count+'; table cells checked: '+$tableCellChecks)
 Write-Output $pptxPath
 Write-Output $pdfPath
}finally{
 if($pres){$pres.Close();[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres)|Out-Null}
 if($pp){[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp)|Out-Null}
}
